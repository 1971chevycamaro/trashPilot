import numpy as np
class SteeringWheelModel:
    def __init__(self, angle=0.0, velocity=0.0, torque=0.0, inertia=0.01, sfriction=4, kfriction=2, damping=0.01, centering=0.04):
        """
        angle     - current angle [deg]
        velocity  - angular velocity [deg/s]
        torque    - applied torque [N·m]
        inertia   - moment of inertia [kg·m²]
        friction  - dry friction torque [N·m]
        damping   - viscous damping coeff [N·m·s/deg]
        centering - proportional centering coefficient (N·m/deg) that produces a restoring torque toward zero angle
        """
        self.angle = angle
        self.velocity = velocity
        self.torque = torque
        self.inertia = inertia
        self.sfriction = sfriction
        self.kfriction = kfriction
        self.damping = damping
        self.centering = centering
        self.net_torque = 0
        self.counter_torque = 0 
    def update(self, dt):
        # Dry friction torque (Coulomb friction)
        # friction_torque = min(abs(-(self.inertia*self.velocity)/dt),self.friction) * -np.sign(self.velocity)
        # apply kinetic friction torque if its more than the torque needed to stop the wheel in a single timestep
        # if we dont do this the applied torque in a timestep can cause the wheel to move too far past zero and oscillate
        friction_torque = min(abs(-(self.inertia*self.velocity)/dt),self.kfriction) * -np.sign(self.velocity)

        # friction_torque = -self.kfriction*np.sign(self.velocity) #unless it causes the velocity to go past zero in which case velocity = 0
        # friction_torque = -(self.inertia*self.velocity)/dt
        # friction_torque = -8*np.sign(self.velocity)
        # friction_torque = max(-self.sfriction,min(-self.torque,self.sfriction)) if abs(self.velocity) < 1 else friction_torque

        # Viscous damping torque
        damping_torque = -self.damping * self.velocity
        # Centering (restoring) torque proportional to angle
        centering_torque = -self.centering * self.angle

        # Net torque on the wheel
        self.net_torque = (self.torque if abs(self.torque) > self.sfriction or abs(self.velocity) > 500 else 0) + friction_torque + damping_torque + centering_torque
        # self.counter_torque = self.net_torque - self.torque
        # self.sfriction_torque = -self.torque if abs(self.velocity) < 10 else 0
        # Angular acceleration (°/s²)
        accel = (self.net_torque / self.inertia)

        # Integrate velocity and angle
        
        self.velocity += accel * dt
        self.angle += self.velocity * dt