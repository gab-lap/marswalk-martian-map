"""Planner-only Nav2 test. Usage: ros2 launch planner_only.launch.py map:=/abs/path/rover_cost.yaml"""
import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    here = os.path.dirname(os.path.realpath(__file__))
    params = os.path.join(here, "planner_params.yaml")
    return LaunchDescription([
        DeclareLaunchArgument("map", description="absolute path to rover_cost.yaml"),
        Node(package="nav2_map_server", executable="map_server", name="map_server", output="screen",
             parameters=[{"yaml_filename": LaunchConfiguration("map")}]),
        # The costmap needs a robot pose frame; a fixed map->base_link transform is enough for planning.
        Node(package="tf2_ros", executable="static_transform_publisher",
             arguments=["--frame-id", "map", "--child-frame-id", "base_link"]),
        Node(package="nav2_planner", executable="planner_server", name="planner_server",
             output="screen", parameters=[params]),
        Node(package="nav2_lifecycle_manager", executable="lifecycle_manager", name="lifecycle_manager",
             output="screen", parameters=[{"autostart": True, "node_names": ["map_server", "planner_server"]}]),
    ])
