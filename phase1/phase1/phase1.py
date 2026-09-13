import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
import cmath

class TurtleController(Node):
    def __init__(self):
        super().__init__('turtleController')

        self.goal = self.declare_parameter('goal', [0.0, 0.0])
        self.start = self.declare_parameter('start', [0.0, 0.0, 0.0])
        self.target = [self.goal.value[i] + self.start.value[i] for i in range(2)]

        self.publisher = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )

        self.subscriber = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.updatePosn,
            10
        )

        self.error = 0.1
        self.timerTime = 0.1
        self.finished = False
        self.x = self.start.value[0]
        self.y = self.start.value[1]
        
        if len(self.start.value) == 2:
            self.theta = 0.0
        else:
            self.theta = self.start.value[2]

        self.timer = self.create_timer(self.timerTime, self.move)

    def magn(self, vec):
        return (vec[0]**2 + vec[1]**2)**0.5

    def sign(self, n):
        if n == 0:
            return 0.0
        else:
            return float(abs(n)/n)

    def move(self):
        dirn = self.target[0] - self.x + (self.target[1] - self.y)*1j

        if abs(dirn) <= self.error:
            self.publisher.publish(Twist())
            self.finished = True
        else:
            msg = Twist()

            if abs(cmath.phase(dirn) - self.theta) <= 0.2:
                msg.linear.x = 1.0
            else:
                msg.angular.z = self.sign(cmath.phase(dirn) - self.theta)

            self.publisher.publish(msg)

    def updatePosn(self, msg):
        self.x = msg.x
        self.y = msg.y
        self.theta = msg.theta

def main():
    rclpy.init()
    node = TurtleController()
    while not node.finished:
        rclpy.spin_once(node)

    node.destroy_node()
    rclpy.shutdown()
