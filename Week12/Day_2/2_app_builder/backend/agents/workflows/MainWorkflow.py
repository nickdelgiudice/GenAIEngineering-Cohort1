# This file contains the implementation of the MainWorkflow.
import logging
from backend.agents.DataProcessingAgent import DataProcessingAgent

class MainWorkflow:
    """
    Primary workflow for the product, orchestrating multiple steps.
    """

    def __init__(self):
        self.logger = logging.getLogger("MainWorkflow")
        self.data_processor = DataProcessingAgent()

    def input_step(self, data):
        """
        Initial step to input and preprocess data.
        """
        self.logger.debug("Executing input step with data: %s", data)
        # Example of data preprocessing
        return data

    def process_step(self, data):
        """
        Processing step to execute main data operations.
        """
        self.logger.debug("Executing process step")
        self.data_processor.data_validation(data)
        self.data_processor.processing(data)

    def output_step(self, data):
        """
        Final step to analyze and output data.
        """
        self.logger.debug("Executing output step")
        self.data_processor.analysis(data)

    def execute(self, data):
        """
        Execute the full workflow.
        """
        self.logger.debug("Starting MainWorkflow execution")
        input_data = self.input_step(data)
        self.process_step(input_data)
        self.output_step(input_data)