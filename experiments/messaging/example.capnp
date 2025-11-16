@0xbf5147cbbecf40e9;
struct Event {
  logMonoTime @0 :UInt64;   # optional metadata

  union {
    status     @1 :Status;
    carControl @2 :CarControl;
    carState   @3 :CarState;
  }
}

struct Status {
  id @0 :Int32;
  name @1 :Text;
  value @2 :Float32;
}
# copied from openpilot 

struct OnroadEventDEPRECATED {
  enum EventName { dummy @0; }
}

struct CarControl {
  # must be true for any actuator commands to work
  enabled @0 :Bool;
  latActive @11: Bool;
  longActive @12: Bool;

  # Final actuator commands
  actuators @6 :Actuators;

  # Blinker controls
  leftBlinker @15: Bool;
  rightBlinker @16: Bool;

  orientationNED @13 :List(Float32);
  angularVelocity @14 :List(Float32);
  currentCurvature @17 :Float32;  # From vehicle model

  cruiseControl @4 :CruiseControl;
  hudControl @5 :HUDControl;

  struct Actuators {
    # lateral commands, mutually exclusive
    torque @2: Float32;  # [0.0, 1.0]
    steeringAngleDeg @3: Float32;
    curvature @7: Float32;

    # longitudinal commands
    accel @4: Float32;  # m/s^2
    longControlState @5: LongControlState;

    # these are only for logging the actual values sent to the car over CAN
    gas @0: Float32;   # [0.0, 1.0]
    brake @1: Float32; # [0.0, 1.0]
    torqueOutputCan @8: Float32;   # value sent over can to the car
    speed @6: Float32;  # m/s

    enum LongControlState @0xe40f3a917d908282{
      off @0;
      pid @1;
      stopping @2;
      starting @3;
    }
  }

  struct CruiseControl {
    cancel @0: Bool;
    resume @1: Bool;
    override @4: Bool;
    speedOverrideDEPRECATED @2: Float32;
    accelOverrideDEPRECATED @3: Float32;
  }

  struct HUDControl {
    speedVisible @0: Bool;
    setSpeed @1: Float32;
    lanesVisible @2: Bool;
    leadVisible @3: Bool;
    visualAlert @4: VisualAlert;
    rightLaneVisible @6: Bool;
    leftLaneVisible @7: Bool;
    rightLaneDepart @8: Bool;
    leftLaneDepart @9: Bool;
    leadDistanceBars @10: Int8;  # 1-3: 1 is closest, 3 is farthest. some ports may utilize 2-4 bars instead

    # not used with the dash, TODO: separate structs for dash UI and device UI
    audibleAlert @5: AudibleAlert;

    enum VisualAlert {
      # these are the choices from the Honda
      # map as good as you can for your car
      none @0;
      fcw @1;
      steerRequired @2;
      brakePressed @3;
      wrongGear @4;
      seatbeltUnbuckled @5;
      speedTooHigh @6;
      ldw @7;
    }

    enum AudibleAlert {
      none @0;

      engage @1;
      disengage @2;
      refuse @3;

      warningSoft @4;
      warningImmediate @5;

      prompt @6;
      promptRepeat @7;
      promptDistracted @8;
    }
  }

  gasDEPRECATED @1 :Float32;
  brakeDEPRECATED @2 :Float32;
  steeringTorqueDEPRECATED @3 :Float32;
  activeDEPRECATED @7 :Bool;
  rollDEPRECATED @8 :Float32;
  pitchDEPRECATED @9 :Float32;
  actuatorsOutputDEPRECATED @10 :Actuators;
}

struct CarState {
  # CAN health
  canValid @26 :Bool;       # invalid counter/checksums
  canTimeout @40 :Bool;     # CAN bus dropped out
  canErrorCounter @48 :UInt32;

  # process meta
  cumLagMs @50 :Float32;

  # car speed
  vEgo @1 :Float32;            # best estimate of speed
  aEgo @16 :Float32;           # best estimate of aCAN cceleration
  vEgoRaw @17 :Float32;        # unfiltered speed from wheel speed sensors
  vEgoCluster @44 :Float32;    # best estimate of speed shown on car's instrument cluster, used for UI

  vCruise @53 :Float32;        # actual set speed
  vCruiseCluster @54 :Float32; # set speed to display in the UI

  yawRate @22 :Float32;     # best estimate of yaw rate
  standstill @18 :Bool;
  wheelSpeeds @2 :WheelSpeeds;

  gasPressed @4 :Bool;    # this is user pedal only

  # brake pedal, 0.0-1.0
  brake @5 :Float32;      # this is user pedal only
  brakePressed @6 :Bool;  # this is user pedal only
  regenBraking @45 :Bool; # this is user pedal only
  parkingBrake @39 :Bool;
  brakeHoldActive @38 :Bool;

  # steering wheel
  steeringAngleDeg @7 :Float32;
  steeringAngleOffsetDeg @37 :Float32; # Offset between sensors in case there multiple
  steeringRateDeg @15 :Float32;    # optional
  steeringTorque @8 :Float32;      # Native CAN units, only needed on cars where it's used for control
  steeringTorqueEps @27 :Float32;  # Native CAN units, only needed on cars where it's used for control
  steeringPressed @9 :Bool;        # is the user overring the steering wheel?
  steeringDisengage @58 :Bool;     # more force than steeringPressed, disengages for applicable brands
  steerFaultTemporary @35 :Bool;
  steerFaultPermanent @36 :Bool;

  invalidLkasSetting @55 :Bool;    # stock LKAS is incorrectly configured (i.e. on or off)
  stockAeb @30 :Bool;
  stockLkas @59 :Bool;
  stockFcw @31 :Bool;
  espDisabled @32 :Bool;
  accFaulted @42 :Bool;
  carFaultedNonCritical @47 :Bool;  # some ECU is faulted, but car remains controllable
  espActive @51 :Bool;
  vehicleSensorsInvalid @52 :Bool;  # invalid steering angle readings, etc.
  lowSpeedAlert @56 :Bool;  # lost steering control due to a dynamic min steering speed
  blockPcmEnable @60 :Bool;  # whether to allow PCM to enable this frame

  # cruise state
  cruiseState @10 :CruiseState;

  # gear
  gearShifter @14 :GearShifter;

  # button presses
  buttonEvents @11 :List(ButtonEvent);
  buttonEnable @57 :Bool;  # user is requesting enable, usually one frame. set if pcmCruise=False
  leftBlinker @20 :Bool;
  rightBlinker @21 :Bool;
  genericToggle @23 :Bool;

  # lock info
  doorOpen @24 :Bool;           # ideally includes all doors
  seatbeltUnlatched @25 :Bool;  # driver seatbelt

  # blindspot sensors
  leftBlindspot @33 :Bool;  # Is there something blocking the left lane change
  rightBlindspot @34 :Bool; # Is there something blocking the right lane change

  fuelGauge @41 :Float32; # battery or fuel tank level from [0.0, 1.0]
  charging @43 :Bool;

  struct WheelSpeeds {
    # optional wheel speeds
    fl @0 :Float32;
    fr @1 :Float32;
    rl @2 :Float32;
    rr @3 :Float32;
  }

  struct CruiseState {
    enabled @0 :Bool;
    speed @1 :Float32;
    speedCluster @6 :Float32;  # Set speed as shown on instrument cluster
    available @2 :Bool;
    standstill @4 :Bool;
    nonAdaptive @5 :Bool;

    speedOffsetDEPRECATED @3 :Float32;
  }

  enum GearShifter {
    unknown @0;
    park @1;
    drive @2;
    neutral @3;
    reverse @4;
    sport @5;
    low @6;
    brake @7;
    eco @8;
    manumatic @9;
  }

  # send on change
  struct ButtonEvent {
    pressed @0 :Bool;
    type @1 :Type;

    enum Type {
      unknown @0;
      leftBlinker @1;
      rightBlinker @2;
      accelCruise @3;
      decelCruise @4;
      cancel @5;
      lkas @6;
      altButton2 @7;
      mainCruise @8;
      setCruise @9;
      resumeCruise @10;
      gapAdjustCruise @11;
    }
  }

  # deprecated
  errorsDEPRECATED @0 :List(OnroadEventDEPRECATED.EventName);
  gasDEPRECATED @3 :Float32;        # this is user pedal only
  brakeLightsDEPRECATED @19 :Bool;
  steeringRateLimitedDEPRECATED @29 :Bool;
  canMonoTimesDEPRECATED @12: List(UInt64);
  canRcvTimeoutDEPRECATED @49 :Bool;
  eventsDEPRECATED @13 :List(OnroadEventDEPRECATED);
  clutchPressedDEPRECATED @28 :Bool;
  engineRpmDEPRECATED @46 :Float32;
}
