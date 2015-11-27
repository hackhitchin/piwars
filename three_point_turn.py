#!/usr/bin/env python
import sys
import logging
import time
import drivetrain


def run():
    # Set up logging
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    # Initiate the drivetrain
    drive = drivetrain.DriveTrain(pwm_i2c=0x41)
    drive.mix_channels_and_assign(throttle, steering)

    # Pseudo Code
#    initiate camera
#    t=0
#    While t<TFirstSegmentTimeout Or RearLineSensor=Red   //forward to turning point
#        If T<TacceleratingFirstSegment
#            Ease throttle to FullForward
#        Else	
#            Ease throttle to SlowForward
#        end If
#        LeftMotor=throttle
#        RightMotor=throttle
#       Get RearLinesensorValue
#    Wend
#
#If throttle Not slow  //must have got better than usual acceleration. need to slow down before changing direction
#	ease throttle to SlowForward
#Fend
#t=0
#While T<TLeftTurnTime  //First Left turn#
#	LeftMotor=stopped
#	If T<TacceleratingSecondSegment
#		Ease RightMotor to FullForward
#	Else	
#		Ease RightMotor to SlowForward
#	end If
#wend
#t=0
#While t<TThirdSegmentTimeout Or FrontLineSensor=Red  //forward to first side line
#	If T<TacceleratingThirdSegment
#		Ease throttle to FullForward
#	Else	
#		Ease throttle to SlowForward
#	end If
#	LeftMotor=throttle
#	RightMotor=throttle
#	Get FrontLinesensorValue
#Wend
#
#If throttle Not slow  //must have got better than usual acceleration. need to slow down before changing direction
#	ease throttle to slow
#Fend
#t=0
#While t<TForthSegmentTimeout Or RearLineSensor=Red  //reverse portion to second side line
#	If T<TacceleratingForthSegment
#		Ease throttle to FullReverse
#	Else	
#		Ease throttle to SlowReverse
#	end If
#	LeftMotor=throttle
#	RightMotor=throttle
#	Get RearLinesensorValue
#Wend
#
#If throttle Not slow  //must have got better than usual acceleration. need to slow down before changing direction
#	ease throttle to SlowReverse
#Fend
#t=0
#While t<TFifthSegmentTimeout  //return to centre of turning area
#	If T<TacceleratingFifthSegment
#		Ease throttle to FullForward
#	Else	
#		Ease throttle to SlowForward
#	end If
#	LeftMotor=throttle
#	RightMotor=throttle
#Wend
#t=0
#While T<TLeftTurnTime  //turn back to centre#
#	LeftMotor=stopped#
#	RightMotor=FullForward
#wend
#t=0
#while t<TLastsegmentTimeout and FrontLineSensor=Red//return to start
#	If T<TacceleratingFinalSegment
#		Ease throttle to FullForward
#	Else	
#		Ease throttle to SlowForward
#	end If
#	Get BeaconAngle
#	steering proportional to BeaconAngle
#	LeftMotor=throttle-max(0,steering)  //only subtract steering from one side, so still works at top speed
#	RightMotor=throttle-max(0,steering)
#Wend
#t=
#while t<TFinishBox and RearLineSensor=Red    //enter box
#	If T<TacceleratingBoxSegment
#		Ease throttle to FullForward   //won't get to full speed but worth smoothly accelerating
#	Else	
#		Ease throttle to SlowForward
#	end If
#	Get BeaconAngle
#	steering proportional to BeaconAngle  //may want different or zero gain whilst in box
#	LeftMotor=throttle-max(0,steering)  //only subtract steering from one side, so still works at top speed
#	RightMotor=throttle-max(0,steering)
#Wend
#t=0
#While t<Tcrossingline
#	Leftmotor=SlowForward
#	RightMotor=SlowForward
#Wend
#LeftMotor=Stopped
#RightMotor=stopped



if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        logging.error("Stopping...")
        logging.exception(e)
