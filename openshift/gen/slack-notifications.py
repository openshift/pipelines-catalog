#!/usr/bin/env python3
import subprocess
import sys
import json
import os
from urllib.request import Request, urlopen

image_failure_png = 'https://www.vhv.rs/dpng/d/415-4154815_grumpy-cat-png-photos-grumpy-cat-png-transparent.png'
image_success_png = 'https://github.com/tektoncd.png'

label_to_search = "nightly-ci"
{% raw -%}
labels = eval("""{{pull_request.labels}}""")
console_url = """{{openshift_console_pipelinerun_href}}"""
pull_request_url = """{{pull_request.html_url}}"""
{% endraw %}

# Check if the PR has nightly CI
isnightly_ci = [x for x in labels if x['name'] == label_to_search]

if not isnightly_ci:
    print("Not a nightly CI PR: skipping the reporting to slack")
    sys.exit(0)

# Check the status of the pipelinerun
ret = subprocess.run(
    f"kubectl get pipelinerun {os.environ.get('PIPELINERUN', 'unkown')} -o json",
    shell=True,
    check=True,
    capture_output=True)

if ret.returncode != 0:
    print("Error retrieving pipelinerun status")
    sys.exit(1)

pr = json.loads(ret.stdout)
# The Running is safe here, because it's the finally task where we are at.
failed = []
taskRuns = pr['status']['taskRuns']
for task in taskRuns.keys():
    if len([
            x['message'] for x in taskRuns[task]['status']['conditions']
            if x['status'] != 'Running' and x['status'] == 'False'
    ]) > 0:
        failed.append(task)

if failed:
    subject = f"OpenShift Pipelines CI has failed on {pull_request_url} " \
        ":fb-sad: :crying_cat_face: :crying:"
    image_url = image_failure_png
    text = f"""• *Failed Tasks*: {", ".join(failed)}
• *PipelineRun logs*: {console_url}
  """
else:
    subject = f"OpenShift Pipelines CI ran succesfully on {pull_request_url} " \
        ":pipelinedance: :dancing-penguin: :yay2:"
    image_url = image_success_png
    text = f"""
    • *PipelineRun logs*: {console_url}
  """

msg = {
    "text":
    subject,
    "attachments": [{
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": text,
                },
                "accessory": {
                    "type": "image",
                    "image_url": image_url,
                    "alt_text": "TektonCD CI"
                }
            },
        ]
    }]
}
req = Request(os.environ.get("SLACK_WEBHOOK_URL"),
              data=json.dumps(msg).encode(),
              headers={"Content-type": "application/json"},
              method="POST")
# TODO: Handle error?
print(urlopen(req).read().decode())
print("slack message has been sent")
