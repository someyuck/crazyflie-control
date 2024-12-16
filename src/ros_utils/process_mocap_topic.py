import argparse
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import String


# just for testing
class ChatterProcessor(Node):
    def __init__(self, topic: str = "/chatter"):
        super().__init__("chatter_processor")
        self.topic = topic
        self.subscription = self.create_subscription(
            String, self.topic, self.chatter_callback, 10
        )

    def chatter_callback(self, msg):
        self.get_logger().info(f"Received message: {msg.data}")


class MocapPoseProcessor(Node):
    """Listener node for a ROS2 pose topic published by a `vrpn_mocap`
    client node. Modify the class to integrate with drone control if needed.
    """

    def __init__(self, topic: str):
        super().__init__("mocap_pose_processor")
        self.topic = topic

        self.subscription = self.create_subscription(
            PoseStamped, self.topic, self.pose_callback, 10  # QoS profile depth
        )

    def pose_callback(self, msg):
        x = msg.position.x
        y = msg.position.y
        z = msg.position.z

        # quaternion
        qx = msg.orientation.x
        qy = msg.orientation.y
        qz = msg.orientation.z
        qw = msg.orientation.w

        # log for now
        self.get_logger().info(f"Position: ({x}, {y}, {z})")
        self.get_logger().info(f"Orientation Quaternion: ({qx}, {qy}, {qz}, {qw})")


def main(topic: str, args=None):
    rclpy.init(args=args)
    # chatter_processor = ChatterProcessor(topic=topic)
    pose_processor = MocapPoseProcessor(topic=topic)

    try:
        # rclpy.spin(chatter_processor)
        rclpy.spin(pose_processor)
    except KeyboardInterrupt:
        pass
    finally:
        # chatter_processor.destroy_node()
        pose_processor.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Input the ros2 topic to listen to")
    parser.add_argument("--topic", type=str, help="ros2 topic", required=True)
    args = parser.parse_args()
    # "/vrpn_mocap/{tracker_name}/pose"
    main(topic=args.topic)
