"""
Take a general request and a specific request with model requirements and build as many requests as params
Both are yaml files
"""

import yaml
import os
import sys

import argparse

def load_yaml(file):
    with open(file) as f:
        return yaml.load(f, Loader=yaml.FullLoader)

def _parse_args():
    parser = argparse.ArgumentParser(description='Build requests')
    parser.add_argument('--general', type=str, default="general_request.yaml", help='General request yaml file')
    parser.add_argument('--model', type=str, default="neuralgcm.yaml", help='Specific request yaml file')
    parser.add_argument('--output', type=str, default=".", help='Output directory')
    return parser.parse_args()

def main():
    args = _parse_args()
    general = load_yaml(args.general)
    model = load_yaml(args.model)

    number_of_params = 0

    for levtype in model['levtype']:
        print(levtype)
        for param in model['levtype'][levtype]:
            number_of_params += 1
            # build request for that param
            request = general.copy()
            request['param'] = param

            # if specified, add model specific requirements
            if 'levelist' in model['levtype'][levtype]:
                request['levelist'] = model['levtype'][levtype]['levelist']
            if 'date' in model['levtype'][levtype]:
                request['date'] = model['levtype'][levtype]['date']
            if 'time' in model['levtype'][levtype]:
                request['time'] = model['levtype'][levtype]['time']

            # save request
            output = os.path.join(args.output, f"request_{number_of_params}.yaml")
            with open(output, 'w') as f:
                yaml.dump(request, f)
            print(f"Saved request to {output}")


    print(model)

if __name__ == '__main__':
    main()
