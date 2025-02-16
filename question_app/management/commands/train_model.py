from django.core.management.base import BaseCommand
from train import train_process

class Command(BaseCommand):
    help = 'Trains the model by processing GitHub issues and creating embeddings'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting model training process...')
        try:
            train_process()
            self.stdout.write(self.style.SUCCESS('Successfully trained the model'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error training model: {str(e)}'))