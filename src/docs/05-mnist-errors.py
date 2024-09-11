
import ray

@ray.remote
def train_fn():
    import os
    import numpy as np
    from datasets import load_dataset, load_metric
    import transformers
    from transformers import (
        Trainer,
        TrainingArguments,
        AutoTokenizer,
        AutoModelForSequenceClassification,
    )
    import ray.train.huggingface.transformers
    from ray.train import ScalingConfig
    from ray.train.torch import TorchTrainer

    # When running in a multi-node cluster you will need persistent storage that is accessible across all worker nodes. 
    # See www.github.com/project-codeflare/codeflare-sdk/tree/main/docs/s3-compatible-storage.md for more information.
    
    def train_func():
        # Datasets
        dataset = load_dataset("imdb")
        tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")

        def tokenize_function(examples):
            return tokenizer(examples["text"], padding="max_length", truncation=True)

        small_train_dataset = (
            dataset["train"].select(range(100)).map(tokenize_function, batched=True)
        )
        small_eval_dataset = (
            dataset["test"].select(range(100)).map(tokenize_function, batched=True)
        )

        # Model
        model = AutoModelForSequenceClassification.from_pretrained(
            "distilbert-base-uncased", num_labels=2
        )

        def compute_metrics(eval_pred):
            metric = load_metric("accuracy")
            logits, labels = eval_pred
            predictions = np.argmax(logits, axis=-1)
            return metric.compute(predictions=predictions, references=labels)

        # Hugging Face Trainer
        training_args = TrainingArguments(
            output_dir="test_trainer",
            evaluation_strategy="epoch",
            save_strategy="epoch",
            report_to="none",
        )

        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=small_train_dataset,
            eval_dataset=small_eval_dataset,
            compute_metrics=compute_metrics,
        )


        callback = ray.train.huggingface.transformers.RayTrainReportCallback()
        trainer.add_callback(callback)

        trainer = ray.train.huggingface.transformers.prepare_trainer(trainer)

        trainer.train()


    ray_trainer = TorchTrainer(
        train_func,
        scaling_config=ScalingConfig(
            # num_workers = number of worker nodes with the ray head node included
            num_workers=1,
            use_gpu=True,
            resources_per_worker={
                "CPU": 1,
            },
            trainer_resources={
                "CPU": 0,
            }
        )
        # Configure persistent storage that is accessible across 
        # all worker nodes.
        # Uncomment and update the RunConfig below to include your storage details.
        # run_config=ray.train.RunConfig(storage_path="storage path"),
    )
    result: ray.train.Result = ray_trainer.fit()

runtime_env = {"pip": ["transformers==4.41.2", "datasets==2.17.0", "accelerate==0.31.0", "scikit-learn==1.5.0"]}
runtime_env = {"pip": ["transformers", "datasets", "accelerate", "scikit-learn"]}
ray_cluster_uri="http://localhost:8265"
# ray.init(address=ray_cluster_uri, runtime_env=runtime_env)
ray.init(num_cpus=4, num_gpus=1, runtime_env=runtime_env)
print(ray.cluster_resources())
ray.get(train_fn.remote())

