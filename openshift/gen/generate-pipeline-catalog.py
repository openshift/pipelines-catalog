#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Chmouel Boudjnah <chmouel@chmouel.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import argparse
import sys
from pathlib import Path

import jinja2
import yaml

SERVICE_ACCOUNT_PRIV = 'pipeline'


def debug(stringy):
    sys.stderr.write(stringy + "\n")


def read_metadata_name(yamlfile):
    with open(yamlfile) as stream:
        return [doc['metadata']['name'] for doc in yaml.safe_load_all(stream)]


def read_resource_name_type(yamlfile):
    with open(yamlfile) as stream:
        return [(doc['spec']['type'], doc['metadata']['name'])
                for doc in yaml.safe_load_all(stream)]


def check_document_start(text):
    if text[0:3] != "---":
        text = "---\n" + text
    return text


def check_no_doublons(filep, listp, filet):
    if filet == 'step':
        for doc in yaml.safe_load_all(filep.open()):
            _names = [s['name'] for s in doc]
    else:
        _names = read_metadata_name(filep)

    for name in _names:
        if name in listp:
            debug(
                f"ERROR: In file {filep}, we saw the {filet} '{name}' already."
            )
            sys.exit(1)
        listp.append(name)
    return listp


# add_pre_steps add a runAfter {stepname} for {step}, so making sure that every
# steps run only after that
def add_pre_steps(steps, stepname):
    step_dic = yaml.safe_load(steps.read_text())
    first_step = step_dic[0]
    if 'runAfter' in first_step:
        first_step['runAfter'].extend(stepname)
    else:
        first_step['runAfter'] = stepname
    step_dic[0] = first_step
    return yaml.dump(step_dic)


def process_task(taskdir,
                 pipeline_name,
                 pipelinetemplate,
                 presteptemplate,
                 privileged=False):
    ret = []
    steps = []
    steps_names = []
    workspaces = []
    workspaces_names = []
    resources = []
    resources_names = []

    if presteptemplate.exists():
        steps.append(presteptemplate.read_text())

    for path in taskdir.glob("*/*/tests"):
        taskdir = Path(str(path).replace("/tests", ""))
        taskname, taskversion = path.parts[1:3]
        config_file = path / "config.yaml"
        config = {}
        if config_file.exists():
            config = yaml.safe_load(open(config_file))

        if not privileged and 'privileged' in config and config['privileged']:
            debug(f"Skipping {taskname} we want non-priv and it's priv")
            continue
        if privileged and 'privileged' not in config:
            debug(f"Skipping {taskname} we want priv and it's non-priv")
            continue

        task = taskdir / f"{taskname}.yaml"
        if not task.exists():
            debug(f"WARNING: Could not find the file {task} skipping")
            continue
        ret.append(check_document_start(task.read_text()))

        run = path / "step.yaml"
        if not run.exists():
            debug(
                f"WARNING: there is no step.yaml file in {taskname}-{taskversion}"
            )
            continue

        debug(f"Adding runstep {run}")
        steps_names = check_no_doublons(run, steps_names, 'step')
        run_text = add_pre_steps(run, ["prestep"])
        steps.append(run_text)

        persistentvolume = path / "pv.yaml"
        if persistentvolume.exists():
            workspaces_names = check_no_doublons(persistentvolume,
                                                 workspaces_names,
                                                 'persistentvolume')
            debug(f"Adding persistentvolume {persistentvolume}")
            workspaces.extend(read_metadata_name(persistentvolume))
            ret.append(check_document_start(persistentvolume.read_text()))

        resource = path / "resource.yaml"
        if resource.exists():
            resources_names = check_no_doublons(resource, resources_names,
                                                'resource')

            debug(f"Adding resource {resource}")
            resources.extend(read_resource_name_type(resource))

        # Add every yaml file verbatim, unless it's a pv/config/run ones which
        # we do differently
        for yamlfile in path.iterdir():
            if yamlfile.suffix != ".yaml":
                continue
            if yamlfile.name.replace(yamlfile.suffix,
                                     "") in ("pv", "config", "step"):
                continue
            debug(f"Adding extras task {yamlfile}")
            ret.append(check_document_start(yamlfile.read_text()))

    template_str = open(pipelinetemplate).read()
    template = jinja2.Environment(loader=jinja2.FileSystemLoader(
        "openshift/gen")).from_string(template_str)
    if privileged:
        service_accountname = SERVICE_ACCOUNT_PRIV
    else:
        service_accountname = ''
    if not steps:
        return ''
    ret.append(
        template.render(steps=steps,
                        config=config,
                        workspaces=workspaces,
                        pipeline_name=pipeline_name,
                        resources=resources,
                        serviceAccountname=service_accountname))

    return "\n".join(ret)


def generate_pipeline(taskdir, pipelinetemplate, presteptemplate):

    print(
        process_task(taskdir,
                     pipelinetemplate=pipelinetemplate,
                     presteptemplate=presteptemplate,
                     pipeline_name="pipelines-catalog",
                     privileged=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("taskdir")
    parser.add_argument("pipelinetemplate")
    parser.add_argument("presteptemplate")
    args = parser.parse_args(sys.argv[1:])
    generate_pipeline(Path(args.taskdir), args.pipelinetemplate,
                      Path(args.presteptemplate))
