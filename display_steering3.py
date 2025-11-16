import pygame
import class_messaging as messaging
import numpy as np
import zmq
import capnp
from  class_steering_model import SteeringWheelModel
import time

def draw_torque_graph(screen, torque_history):
    graph_height = 100
    graph_bottom = screen.get_height() - graph_height//2 - 20
    graph_left = 20
    graph_width = screen.get_width() - 40
    if len(torque_history) < 2:
        return
    
    # Scale torque values to fit in graph area
    max_torque = 10  # expected torque range (adjust for your system)
    
    points = []
    for i, tau in enumerate(torque_history):
        x = graph_left + i * (graph_width / max_points)
        y = graph_bottom - (tau / max_torque) * (graph_height / 2)
        points.append((x, y))
    
    # Draw line
    pygame.draw.lines(screen, (100,255,100), False, points, 2)
    
    # Draw axis
    pygame.draw.line(screen, (100, 100, 100),
                     (graph_left, graph_bottom),
                     (graph_left + graph_width, graph_bottom))

sm = messaging.SubMaster('modelV2')
example_capnp = capnp.load('experiments/messaging/example.capnp')
ctx = zmq.Context()
pub = ctx.socket(zmq.PUB)
pub.bind("tcp://*:5558") # publish carControl

sub = ctx.socket(zmq.SUB)
sub.setsockopt_string(zmq.SUBSCRIBE, "")
sub.setsockopt(zmq.CONFLATE, 1)
sub.connect("tcp://localhost:5556") # subscribe carState

steeringWheel = SteeringWheelModel(inertia=0.01, centering=0.05,damping=0.1,sfriction=0,kfriction=0.7)
desiredAngle = 0
control_enabled = False
disable_timer = 0.0
angle = 0
curv = 0
vEgo = 5.0
dt = 0
setup = False
# Create a list to store recent torque values
torque_history = []
max_points = 200  # how many frames to keep in the graph

pygame.font.init()

pygame.display.set_caption("trashPilot tool")
pygame.display.set_icon(pygame.image.load("assets/steeringwheel.svg"))
W, H = 400,500
center_x = W // 2
screen = pygame.display.set_mode((W, H),pygame.RESIZABLE)
clock = pygame.time.Clock()
font = pygame.font.SysFont('dejavusansmono', 20)
wheel_asset = pygame.image.load("assets/steeringwheel.svg")   
pygame.event.post(pygame.event.Event(pygame.VIDEORESIZE,{'w':W,'h':H}))  # initial resize event


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
            elif event.key == pygame.K_r:
                steeringWheel.angle = desiredAngle
                steeringWheel.velocity = 0
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



    steeringRatio = -3500
    desiredAngle = curv * steeringRatio
    # PD controller
    if not setup:
        steeringWheel.angle = desiredAngle
        setup = True

    omega = 5.0  # natural frequency of response (~ how fast you want it to move)
    error = desiredAngle - steeringWheel.angle

    # Desired acceleration (critically damped response)
    desired_accel = omega**2 * error - 2 * omega * steeringWheel.velocity

    # Compute required torque to make that acceleration happen
    I = steeringWheel.inertia  # noqa: E741
    tau_ff = I * desired_accel

    # Add friction & damping compensation
    tau_ff += steeringWheel.kfriction * np.sign(steeringWheel.velocity)
    tau_ff += steeringWheel.damping * steeringWheel.velocity
    tau_cmd = tau_ff
    tau_max = 14.0

    # soft saturation with tanh
    tau_sat = tau_max * np.tanh(tau_cmd / tau_max)










    #randomly disable acceration for testing
    if control_enabled and abs(error) < 1:
        steeringWheel.torque = 0
    elif control_enabled and (abs(error) > 1):
        steeringWheel.torque = tau_sat
    # After computing steeringWheel.torque:
    torque_history.append(steeringWheel.torque)

    # Keep buffer size fixed
    if len(torque_history) > max_points:
        torque_history.pop(0)


    rotated = pygame.transform.rotate(wheel, steeringWheel.angle)
    ghost_rotated = pygame.transform.rotate(ghost, desiredAngle)
    
    # print(error)

    # try to get realtime vEgo from socket
    try:
      raw = sub.recv(flags=zmq.NOBLOCK)
      with example_capnp.Event.from_bytes(raw) as msg:
        vEgo = msg.carState.vEgo
    except zmq.Again:
      pass

    text = font.render(f"Error: {error:6.1f} Torque: {steeringWheel.torque:6.1f} {'AUT' if control_enabled else 'MAN'}", True, (255, 255, 255))
    text2 = font.render(f"{vEgo:2.0f} KM/H", True, (255, 255, 255))
    msg = example_capnp.Event.new_message()
    msg.logMonoTime = int(time.monotonic() * 1000)

    msg.init('carControl').actuators.torque = float(steeringWheel.torque)

    pub.send(msg.to_bytes())
    screen.fill((30, 30, 30))
    torqueRatio = (steeringWheel.torque/tau_max)*-center_x
    antiTorqueRatio = ((steeringWheel.net_torque-steeringWheel.torque)/tau_max)*-center_x
    powerRatio = abs((steeringWheel.torque*steeringWheel.velocity)/(tau_max*120)*W)
    pygame.draw.line(screen, (100,255,100), (center_x, 40),(torqueRatio+center_x+1, 40),10)
    pygame.draw.line(screen, (255,100,100), (center_x, 40),(antiTorqueRatio+center_x+1, 40),10)
    pygame.draw.line(screen, (255,255,100), (0, 30),(max(1, powerRatio), 30),10)
    draw_torque_graph(screen, torque_history)
    screen.blit(text, (0, 0))
    screen.blit(text2, (0, 50))
    screen.blit(ghost_rotated, ghost_rotated.get_rect(center=(center_x, wheel.get_height()//2+50 )))
    screen.blit(rotated, rotated.get_rect(center=(center_x, wheel.get_height()//2+50 )))
    pygame.display.flip()
    dt = clock.tick(20) / 1000
    steeringWheel.update(dt)
    
pygame.quit()

