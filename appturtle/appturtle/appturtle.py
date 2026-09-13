import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
import math
from std_srvs.srv import Empty

class TurtleControl(Node):

    def __init__(self):
        super().__init__('appturtle')

        self.publisher = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )

        self.subscriber = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.storePose,
            10
        )

        self.client = self.create_client(
            Empty,
            '/reset'
        )

        self.radii = [1, 1]
        self.movingTwd = 1
        self.angleError = 0.1
        self.angles = [0, math.pi/2, math.pi, -math.pi/2]
        self.baserad = 0.05
        self.paused = False

        self.timer = self.create_timer(0.1, self.move)

    def move(self):
        if not self.paused:
            msg = Twist()
            msg.linear.x = 1.0 * self.baserad * self.radii[-1]
            msg.angular.z = 1.0
            self.publisher.publish(msg)
        else:
            if (self.get_clock().now() - self.time).nanoseconds/1e9 >= 0.5:
                self.paused = False
                self.client.call_async(Empty.Request())
                self.radii = [1, 1]
                self.movingTwd = 1        

    
    def storePose(self, msg):
        self.x = msg.x
        self.y = msg.y
        self.theta = msg.theta
        if abs(self.theta - self.angles[self.movingTwd]) <= self.angleError:
            self.movingTwd = (self.movingTwd+1)%4
            self.radii.append(self.radii[-1] + self.radii[-2])
            self.publisher.publish(Twist())
        
        if not(0 < self.x < 11 and 0 < self.y < 11) and not self.paused:
            self.resetScene()
    
    def resetScene(self):
        self.publisher.publish(Twist())
        self.paused = True
        self.time = self.get_clock().now()

def main():
    rclpy.init()
    node = TurtleControl()
    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
