# Nav2 planner-only test (run natively on Jazzy by the owner, Nov 13; see CHANGELOG)

Goal: confirm Nav2 can plan on the exported rover cost map and avoids blocked cells.

    # 1. make the map files (any machine)
    cd .. && python3 run_demo.py out
    # 2. terminal A (ROS 2 Jazzy, native Ubuntu 24.04)
    source /opt/ros/jazzy/setup.bash
    cd nav2_test && ros2 launch ./planner_only.launch.py map:=$(realpath ../out/rover_cost.yaml)
    # 3. terminal B
    source /opt/ros/jazzy/setup.bash
    python3 send_path.py ../out

Expect: "poses on blocked cells: 0" and a Nav2 length in the same range as the Python rover route
(not identical: Nav2 uses its own cost scaling and inflation). Optional: open RViz2, add Map (/map),
Costmap (/global_costmap/costmap) and a Path display.

If it fails, likely causes: package not installed (`sudo apt install ros-jazzy-nav2-bringup`), lifecycle nodes not
active (check the lifecycle_manager log), costmap waiting for the map->base_link transform, or a params
key mismatch. Send me the log.
