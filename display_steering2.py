import pygame
import class_messaging as messaging
import numpy as np
import sys
import numpy as np

class SteeringWheelModel:
    def __init__(self, angle=0.0, velocity=0.0, torque=0.0, inertia=0.01, friction=0.6, damping=0.1, timestep = 0.01):
        """
        angle     - current angle [deg]
        velocity  - angular velocity [deg/s]
        torque    - applied torque [N·m]
        inertia   - moment of inertia [kg·m²]
        friction  - dry friction torque [N·m]
        damping   - viscous damping coeff [N·m·s/deg]
        """
        self.angle = angle
        self.velocity = velocity
        self.torque = torque
        self.inertia = inertia
        self.friction = friction
        self.damping = damping
        self.timestep = timestep

    def update(self, dt):
        # Dry friction torque (Coulomb friction)
        dt = 10 if dt > 1 else dt
        for i in range(int(dt//self.timestep)):
            if abs(self.velocity) > 1e-3:
                friction_torque = -self.friction * np.sign(self.velocity)
            else:
                # Static friction region
                if abs(self.torque) < self.friction:
                    friction_torque = -self.torque  # cancel torque — stays still
                else:
                    friction_torque = -self.friction * np.sign(self.torque)

            # Viscous damping torque
            damping_torque = -self.damping * self.velocity

            # Net torque on the wheel
            net_torque = self.torque + friction_torque + damping_torque

            # Angular acceleration (°/s²)
            accel = (net_torque / self.inertia)

            # Integrate velocity and angle
            # dt//1
        
            self.velocity += accel * self.timestep
            self.angle += self.velocity * self.timestep

def draw_torque_graph(screen, torque_history):
    graph_height = 100
    graph_bottom = screen.get_height() - graph_height//2 - 20
    graph_left = 20
    graph_width = screen.get_width() - 40
    if len(torque_history) < 2:
        return
    
    # Scale torque values to fit in graph area
    max_torque = 10  # expected torque range (adjust for your system)
    scale_y = graph_height / (2 * max_torque)  # scale for ±max_torque
    
    points = []
    for i, tau in enumerate(torque_history):
        x = graph_left + i * (graph_width / max_points)
        y = graph_bottom - (tau * scale_y * graph_height / graph_height) - (graph_height / 2)
        y = graph_bottom - (tau / max_torque) * (graph_height / 2)
        points.append((x, y))
    
    # Draw line
    pygame.draw.lines(screen, (100,255,100), False, points, 2)
    
    # Draw axis
    pygame.draw.line(screen, (100, 100, 100),
                     (graph_left, graph_bottom),
                     (graph_left + graph_width, graph_bottom))
pygame.display.set_caption("trashPilot tool")
pygame.display.set_icon(pygame.image.load("assets/steeringwheel.svg"))
pygame.font.init()
sm = messaging.SubMaster('modelV2')
W, H = 400,500
center_x = W // 2
screen = pygame.display.set_mode((W, H))

clock = pygame.time.Clock()

font = pygame.font.SysFont('dejavusansmono', 20)
# wheel = pygame.font.SysFont("segoeuisymbol", 300)  # large font
wheel_asset = pygame.image.load("assets/steeringwheel.svg")   
pygame.event.post(pygame.event.Event(pygame.VIDEORESIZE,{'w':W,'h':H}))  # initial resize event
symbol = "⎉"
steeringWheel = 0
control_enabled = True
disable_timer = 0.0
angle = 0
curv =0
dt = 0
setup = False
# Create a list to store recent torque values
torque_history = []
max_points = 200  # how many frames to keep in the graph


# Example usage:
steeringWheel = SteeringWheelModel(angle=0)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # This triggers when you click the window's X
            running = False
        # Toggle control manually with SPACE
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                control_enabled = not control_enabled
                steeringWheel.torque = 0
            elif event.key == pygame.K_LEFT:
                last_control_enabled = control_enabled

                control_enabled = False
                steeringWheel.torque = 8
            elif event.key == pygame.K_RIGHT:
                last_control_enabled = control_enabled
                control_enabled = False
                steeringWheel.torque = -8
            
        elif event.type == pygame.KEYUP:
            
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                control_enabled = last_control_enabled
                steeringWheel.torque = 0
        elif event.type == pygame.VIDEORESIZE:
            W, H = event.w, event.h
            center_x = W // 2
            dim = min(W-50, H- 160) 
            wheel = pygame.transform.smoothscale(wheel_asset, (dim, dim))
            ghost = wheel.copy()
            ghost.set_alpha(80)


            # screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)  
    if sm.updated():
        curv = sm.data()['action'][0]



    desired_angle = curv * -5000
    # PD controller
    if not setup:
        steeringWheel.angle = desired_angle
        setup = True

    omega = 5.0  # natural frequency of response (~ how fast you want it to move)
    error = desired_angle - steeringWheel.angle

    # Desired acceleration (critically damped response)
    desired_accel = omega**2 * error - 2 * omega * steeringWheel.velocity

    # Compute required torque to make that acceleration happen
    I = steeringWheel.inertia
    tau_ff = I * desired_accel

    # Add friction & damping compensation
    tau_ff += steeringWheel.friction * np.sign(steeringWheel.velocity)
    tau_ff += steeringWheel.damping * steeringWheel.velocity
    tau_cmd = tau_ff
    tau_max = 12.0

    # soft saturation with tanh
    tau_sat = tau_max * np.tanh(tau_cmd / tau_max)










    #randomly disable acceration for testing
    if control_enabled and abs(error) < 2:
        steeringWheel.torque = 0
    elif control_enabled and (abs(error) > 2):
        steeringWheel.torque = tau_sat
    # After computing steeringWheel.torque:
    torque_history.append(steeringWheel.torque)

    # Keep buffer size fixed
    if len(torque_history) > max_points:
        torque_history.pop(0)
    # print(control_enabled)
    # if (-0.5 <= error <= 0.5) and (abs(steeringWheel.velocity) < 0.5):
    #     steeringWheel.torque = 0
    #     steeringWheel.velocity = 0
    #     steeringWheel.angle = 50
    rotated = pygame.transform.rotate(wheel, steeringWheel.angle)
    ghost_rotated = pygame.transform.rotate(ghost, desired_angle)
    
    # print(error)




    text = font.render(f"Error: {error:6.1f} Torque: {steeringWheel.torque:6.1f} {'AUT' if control_enabled else 'MAN'}", True, (255, 255, 255))

    screen.fill((30, 30, 30))
    torque_ratio = (steeringWheel.torque/tau_max)*-center_x
    power_ratio = abs((steeringWheel.torque*steeringWheel.velocity)/(tau_max*120)*W)
    pygame.draw.line(screen, (100,255,100), (center_x, 40),(torque_ratio+center_x+1, 40),10)
    pygame.draw.line(screen, (255,255,100), (0, 30),(max(1, power_ratio), 30),10)
    draw_torque_graph(screen, torque_history)
    screen.blit(text, (0, 0))
    screen.blit(ghost_rotated, ghost_rotated.get_rect(center=(center_x, wheel.get_height()//2+50 )))
    screen.blit(rotated, rotated.get_rect(center=(center_x, wheel.get_height()//2+50 )))
    pygame.display.flip()
    dt = clock.tick(20) / 1000

    steeringWheel.update(dt)
    
pygame.quit()

