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

## Use it
On the Connection menu, click Connect/disconnect. This will open the connection manager. Add site URLs and Master Keys to enable connections.

Click the connection you want and then click OK to connect.

This will list the first page of devices in the left-hand pane. To list all devices, click the **Load all** button.

Click a device in the list to view its available channels.

Use the **Select device** and **Deselect device** buttons to create a list of devices that the program should "actuate" for.

Use the **Start actuating** and **Stop actuating** to turn the background thread on and off. When on, it will loop through the
enabled devices and then loop through their channels. For any channels that begin with "Actuator-8", it will read the values and write them back
to a sensor channel of the same name, but beginning with Sensor-0 instead of Actuator-8. The Actuator-8 channel readings will then be deleted.

This emulates the nPod + IMX consuming the pending actuator writes to its control channels and is designed to work on test or demo devices.

On the Connection menu, click **Status message history** to open up a window displaying status/debug messages.

## Licensing
Please check the LICENSE file within