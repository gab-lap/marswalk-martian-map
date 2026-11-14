"""Ask Nav2's planner for hab -> stop1 -> stop2 -> stop3 on the exported rover map and check the result.
Usage: python3 send_path.py ../out      (needs summary.json, rover_cost.pgm/.yaml from run_demo.py)"""
import json, math, sys
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import ComputePathToPose

out = sys.argv[1] if len(sys.argv) > 1 else "../out"
summ = json.load(open(f"{out}/summary.json"))
meta = dict(l.split(":", 1) for l in open(f"{out}/rover_cost.yaml") if ":" in l)
res = float(meta["resolution"]); ox, oy = [float(v) for v in meta["origin"].strip(" []\n").split(",")[:2]]
with open(f"{out}/rover_cost.pgm", "rb") as f:
    f.readline(); w, h = map(int, f.readline().split()); f.readline(); pix = f.read()

def to_xy(rc):   # array cell (row 0 = top) -> map metres
    return ((rc[1] + 0.5) * res + ox, (h - rc[0] - 0.5) * res + oy)
def to_rc(x, y):
    return (int(h - 1 - math.floor((y - oy) / res)), int(math.floor((x - ox) / res)))

def pose(node, xy):
    p = PoseStamped(); p.header.frame_id = "map"; p.header.stamp = node.get_clock().now().to_msg()
    p.pose.position.x, p.pose.position.y = xy; p.pose.orientation.w = 1.0
    return p

rclpy.init(); node = Node("path_check")
client = ActionClient(node, ComputePathToPose, "compute_path_to_pose")
client.wait_for_server()
wps = [summ["waypoints_rc"]["hab"]] + summ["waypoints_rc"]["stops"]
total, on_blocked = 0.0, 0
for a, b in zip(wps[:-1], wps[1:]):
    goal = ComputePathToPose.Goal(); goal.planner_id = "GridBased"; goal.use_start = True
    goal.start = pose(node, to_xy(a)); goal.goal = pose(node, to_xy(b))
    fut = client.send_goal_async(goal); rclpy.spin_until_future_complete(node, fut)
    gh = fut.result()
    if not gh.accepted: print("goal rejected", a, b); continue
    rf = gh.get_result_async(); rclpy.spin_until_future_complete(node, rf)
    pts = [(p.pose.position.x, p.pose.position.y) for p in rf.result().result.path.poses]
    if len(pts) < 2: print("no path", a, b); continue
    total += sum(math.dist(p, q) for p, q in zip(pts[:-1], pts[1:]))
    for x, y in pts:
        r, c = to_rc(x, y)
        if 0 <= r < h and 0 <= c < w and pix[r * w + c] == 0: on_blocked += 1
print(f"Nav2 rover path length: {total:.0f} m  (python A* rover route: {summ['rover']['length_m']} m)")
print(f"poses on blocked cells: {on_blocked} (should be 0)")
node.destroy_node(); rclpy.shutdown()
