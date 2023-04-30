import mlflow.sklearn

def load_model( model_path="./Model"):
    """
    Loads an sklearn model saved with MLflow.

    Args:
        run_id (str): The ID of the MLflow run that logged the model.
        model_path (str): The relative path of the model directory within the run's artifact directory.

    Returns:
        An sklearn model object.
    """
    # Load the saved model from the artifact directory
    model = mlflow.sklearn.load_model(model_path)
    return model
