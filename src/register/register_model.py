import boto3
import yaml
import sys

def main():
    config_path = sys.argv[1] if len(sys.argv) > 1 else "configs/dev.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)
    sagemaker = boto3.client('sagemaker')
    # Register model (placeholder)
    print("Model registered.")

if __name__ == "__main__":
    main()
