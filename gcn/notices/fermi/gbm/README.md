# Fermi GBM GCN Notices

Fermi GBM is associated with 5 types of public GCN notices:

| Notice Type         | Classic GCN Numeric Type | Kafka/JSON Implementation |
| :------------------ | :----------------------: | :-----------------------: |
| Alert               |            110           | Yes |
| Flight Position     |            111           | No  |
| Ground Position     |            112           | No  |
| Final Position      |            115           | No  |
| Subthreshold Search |            131           | No  |

The classic GCN defines other notice types for the Fermi LAT instrument.  Some Fermi notice types are intended for internal use or testing.

Note that introducing the new JSON format for the Fermi GBM notices doesn't discontinue the classic formats: text, binary, and VOEvent.

## Trigger-Initiated Notice Types

When a GBM trigger occurs, the spacecraft issues an Alert notice withing seconds and a few seconds later a Flight Position notice with an initial Classification and Localization. More Flight Position or other type notices follow, each one improving the localization or classification of the previous one. Typically one Final Position notice will come at the end although more are possible with a human input.  See the following table for more details:

| Notice Type     |  Numeric Type  |      Origin     |  Localization  | Classification | Count | Delay       |
| :-------------- | :------------: | :-------------: | :------------: | :------------: | :---: | :---------- |
| Alert           | 110            | Flight          | No             | No             | 1     | Seconds     |
| Flight Position | 111            | Flight          | Yes            | Yes            | 1+    | 1-2 Minutes |
| Ground Position | 112            | Ground          | Yes            | No             | 0+    | Minutes     |
| Final Position  | 115            | Ground          | Yes            | No             | 0-1   | Minutes     |
| Final Position  | 115            | Human           | Yes            | No             | 0+    | 1+ Hours    |

![](NoticesSequence.jpg)


## Subthreshold Notices

The subthreshold search is looking for transients which didn't cause the flight software to trigger.  It sends out one notice per transient.

| Notice Type  | Numeric Type   | Origin         | Localization | Classification | Count | Delay |
| :----------- | :------------: | :------------: | :----------: | :------------: | :---: | :---- |
| Subthreshold | 131            | Ground         | No           | Yes            | 1     | Hours |
