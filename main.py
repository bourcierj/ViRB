from models.ResNet50Encoder import ResNet50Encoder
from ViRBRunner import ViRBRunner
import argparse
import yaml
import warnings


def main():
    experiment_list = parse_args()
    runner = ViRBRunner(
        experiments={
            name: ResNet50Encoder(weights=weights)
            for name, weights in experiment_list.items()
        },
        train_encoder=False
    )
    runner.run()


def parse_args():
    parser = argparse.ArgumentParser(description='pyTorch ViRB')
    parser.add_argument('--experiment_list', help='Path to file with config of runs')
    parser.add_argument('--name', help='Name of current run')
    parser.add_argument('--encoder_weights', help='Path to the weights of the encoder to use')
    parser.add_argument('--suffix', help='Suffix to be appended to all experiment names', default="")
    args = parser.parse_args()
    if args.experiment_list is not None:
        with open(args.experiment_list) as file:
            experiment_list = yaml.load(file, Loader=yaml.FullLoader)
            experiment_list = {name+args.suffix: data for name, data in experiment_list.items()}
            return experiment_list
    return {args.name+args.suffix: args.encoder_weights}


if __name__ == '__main__':
    main()
