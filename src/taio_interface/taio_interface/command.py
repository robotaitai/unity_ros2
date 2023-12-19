import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import select
import sys
import termios
import tty
import cv2
from sensor_msgs.msg import Image
import numpy as np

class ImagePublisher(Node):
    def __init__(self):
        super().__init__('image_publisher')
        self.publisher_ = self.create_publisher(Image, '/taio/image', 10)
        print("Opening video.")  # Log video open
        self.video = cv2.VideoCapture('/home/taio/code/ros2-for-unity/src/taio_interface/taio_interface/pics/robot.mp4')
        print("Video opened:", self.video.isOpened())  # Log video open status
        self.timer = self.create_timer(0.1, self.publish_frame())  # Adjust the frame rate as needed
        print("Timer created.")  # Log timer creation


    def publish_frame(self):
        ret, frame = self.video.read()
        print("Reading frame:", ret)  # Log frame reading status
        if ret:
            frame = cv2.resize(frame, (640, 480), interpolation=cv2.INTER_LINEAR)
            ros_image = self.cv2_to_imgmsg(frame, encoding="bgr8")
            self.publisher_.publish(ros_image)
            print("Published frame.")  # Log successful publish
        else:
            print("End of video or error reading frame.")  # Log error or end of video
            self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)


    def cv2_to_imgmsg(self, cv_image, encoding="bgr8"):
        # Convert OpenCV image to ROS2 Image message
        msg = Image()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.height = cv_image.shape[0]
        msg.width = cv_image.shape[1]
        msg.encoding = encoding
        msg.is_bigendian = False
        msg.step = int(cv_image.size / cv_image.shape[0])
        msg.data = cv_image.tobytes()
        return msg



class KeyboardController(Node):
    def __init__(self):
        super().__init__('keyboard_controller')
        self.publisher_ = self.create_publisher(Twist, '/taio/command', 10)
        self.settings = termios.tcgetattr(sys.stdin)
        self.key_mappings = {
            'w': (0.1, 0.0),   # Increase forward
            's': (-0.1, 0.0),  # Increase backward
            'a': (0.0, 0.1),   # Increase left
            'd': (0.0, -0.1),  # Increase right
            ' ': (0.0, 0.0),   # Stop
        }
        self.linear = 0.0
        self.angular = 0.0 
        self.image_publisher = ImagePublisher()
        

    def read_key(self):
        tty.setraw(sys.stdin.fileno())
        select.select([sys.stdin], [], [], 0)
        key = sys.stdin.read(1)
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
        return key

    def publish_command(self):
        msg = Twist()
        msg.linear.x = self.linear
        msg.linear.y = self.angular
        self.publisher_.publish(msg)
    
    def run(self):
        try:
            while True:
                key = self.read_key()
                print("Pressed key:", key)  # Log key press
                if key in self.key_mappings:
                    linear_change, angular_change = self.key_mappings[key]
                    self.linear += linear_change
                    self.angular += angular_change
                    print(f"Publishing command: linear={self.linear}, angular={self.angular}")  # Log command values
                    self.publish_command()
                if key == '\x03':
                    break
        except Exception as e:
            print('Exception in keyboard controller:', e)  # Log exceptions
        finally:
            self.publish_command(0.0, 0.0)

def main(args=None):
    rclpy.init(args=args)
    node = KeyboardController()
    node.run()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
