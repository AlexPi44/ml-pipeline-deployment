from sagemaker.workflow.pipeline import Pipeline
from sagemaker.workflow.steps import ProcessingStep, TrainingStep, CreateModelStep
from sagemaker.workflow.parameters import ParameterString
from sagemaker.sklearn.estimator import SKLearn
from sagemaker.processing import ProcessingInput, ProcessingOutput, ScriptProcessor
import yaml

def create_pipeline(config_path="configs/dev.yaml"):
    with open(config_path) as f:
        config = yaml.safe_load(f)
    input_data = ParameterString(
        name="InputData",
        default_value=f"s3://{config['s3']['raw_bucket']}/data/"
    )
    processor = ScriptProcessor(
        image_uri=f"{config['ecr']['registry']}/{config['ecr']['repo']}:train-latest",
        role=config['sagemaker']['role_arn'],
        instance_type="ml.m5.xlarge",
        instance_count=1
    )
    processing_step = ProcessingStep(
        name="FeatureEngineering",
        processor=processor,
        code="src/features/make_features.py",
        inputs=[
            ProcessingInput(source=input_data, destination="/opt/ml/processing/input")
        ],
        outputs=[
            ProcessingOutput(source="/opt/ml/processing/output", destination=f"s3://{config['s3']['features_bucket']}/")
        ]
    )
    sklearn_estimator = SKLearn(
        entry_point="src/train/train.py",
        role=config['sagemaker']['role_arn'],
        instance_type=config['sagemaker']['instance_type'],
        framework_version="1.0-1",
        hyperparameters={"config": "configs/dev.yaml"}
    )
    training_step = TrainingStep(
        name="ModelTraining",
        estimator=sklearn_estimator,
        inputs={
            "train": f"s3://{config['s3']['features_bucket']}/train/"
        }
    )
    pipeline = Pipeline(
        name="MLPipeline",
        steps=[processing_step, training_step]
    )
    return pipeline

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/dev.yaml")
    parser.add_argument("--action", choices=["create", "execute"], default="create")
    args = parser.parse_args()
    pipeline = create_pipeline(args.config)
    if args.action == "execute":
        execution = pipeline.start()
        print(f"Pipeline execution started: {execution.arn}")
