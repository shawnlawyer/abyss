# Add the following imports at the beginning of your code
from kerastuner import HyperModel, RandomSearch, Hyperband, BayesianOptimization
from seq2seq import build
# Create a new class extending HyperModel for Keras Tuner
class ChatbotHyperModel(HyperModel):
    def __init__(self, vocab_size):
        self.vocab_size = vocab_size

    def build(self, hp):
        embedding_size = hp.Int('embedding_size', min_value=32, max_value=256, step=32)
        recurrent_units = hp.Int('recurrent_units', min_value=32, max_value=256, step=32)
        recurrent_layers = hp.Int('recurrent_layers', min_value=1, max_value=3, step=1)
        recurrent_type = hp.Choice('recurrent_type', values=['LSTM', 'GRU'])
        dropout = hp.Float('dropout', min_value=0.0, max_value=0.5, step=0.1)
        recurrent_dropout = hp.Float('recurrent_dropout', min_value=0.0, max_value=0.5, step=0.1)
        learning_rate = hp.Float('learning_rate', min_value=1e-4, max_value=1e-2, sampling='LOG')
        learning_rate_decay = hp.Float('learning_rate_decay', min_value=0.0, max_value=0.99, step=0.01)
        gradient_clip = hp.Float('gradient_clip', min_value=1.0, max_value=5.0, step=0.1)

        return build(self.vocab_size, embedding_size, recurrent_units, recurrent_layers, recurrent_type, dropout, recurrent_dropout, learning_rate, learning_rate_decay, gradient_clip)

# Update the train function to work with Keras Tuner
def train(tuner, train_data, test_data, epochs, callbacks):
    X_train, y_train = train_data
    X_test, y_test = test_data

    return tuner.search(
        X_train,
        y_train,
        epochs=epochs,
        validation_data=(X_test, y_test),
        callbacks=callbacks,
    )

# Set up Keras Tuner and start the search
def start_tuner_search(hypermodel, train_data, test_data, epochs, callbacks, tuner_type="random", max_trials=10, executions_per_trial=1, tuner_directory="tuner", project_name="chatbot", seed=None):
    if tuner_type == "hyperband":
        tuner = Hyperband(
            hypermodel,
            max_epochs=epochs,
            objective='val_loss',
            seed=seed,
            executions_per_trial=executions_per_trial,
            directory=tuner_directory,
            project_name=project_name,
        )
    elif tuner_type == "bayesian":
        tuner = BayesianOptimization(
            hypermodel,
            objective='val_loss',
            seed=seed,
            max_trials=max_trials,
            executions_per_trial=executions_per_trial,
            directory=tuner_directory,
            project_name=project_name,
        )
    else:
        tuner = RandomSearch(
            hypermodel,
            objective='val_loss',
            seed=seed,
            max_trials=max_trials,
            executions_per_trial=executions_per_trial,
            directory=tuner_directory,
            project_name=project_name,
        )

    train(tuner, train_data, test_data, epochs, callbacks)

    # Get the best hyperparameters and model after the search
    best_hyperparameters = tuner.get_best_hyperparameters(num_trials=1)[0]
    best_model = tuner.get_best_models(num_models=1)[0]

    return best_hyperparameters, best_model


# Modify the main function to use the Keras Tuner
def main():
    # ... (keep the data preparation and train-test split code)

    # Create the ChatbotHyperModel instance
    hypermodel = ChatbotHyperModel(vocab_size)

    # Train the model using Keras Tuner
    best_hyperparameters, best_model = start_tuner_search(
        hypermodel,
        train_data,
        test_data,
        epochs,
        callbacks,
        tuner_type="random",
        max_trials=10,
        executions_per_trial=1,
        tuner_directory="tuner",
        project_name="chatbot",
        seed=42
    )

    # Save the best model and print the best hyperparameters
    best_model.save('best_model.h5')
    print("Best hyperparameters found: ", best_hyperparameters)


if __name__ == "__main__":
    main()

