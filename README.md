# ActuatorUpdater

## Intro
ActuatorUpdater is a test tool for the netBin Hub software used to imitate an IMX-connected nPod device's settings 
consumption behaviour.

ActuatorUpdater connects to instances of the netBin Hub using its API and can poll the actuator 
channels of selected devices, write the values to the corresponding sensor channels, and delete from the actuator 
channel, agnostically mimicking the behaviour of a real nPod receiving its configuration updates.

## Get it
The latest version can always be found at [https://github.com/willwybrow/ActuatorUpdater](https://github.com/willwybrow/ActuatorUpdater)

## Install it
After downloading it, make sure the requirements are met either systemwide or in a virtualenv:

`pip install -r requirements.txt`

Then it should be ready to run.

## Run it
`python main.py`

From within your virtual environment if you have one.

## Licensing
Please check the LICENSE file within