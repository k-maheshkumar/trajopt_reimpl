from urdf_parser_py.urdf import URDF
import Planner
import time
from munch import *
from scripts.utils import yaml_paser as yaml


class Robot:
    def __init__(self, urdf_file):

        # location_prefix = '/home/mahesh/libraries/bullet3/data/'
        location_prefix = '/home/mahe/masterThesis/bullet3/data/'

        self.model = URDF.from_xml_file(location_prefix + "kuka_iiwa/model.urdf")
        # self.__replace_joints_in_model_with_map()
        self.state = self.init_state()
        self.planner = {}

    def init_state(self):
        state = {}
        for joint in self.model.joints:
            state[joint.name] = {
                                    "current_value": 0
                                }
        state = munchify(state)
        return state

    def get_state(self):
        return self.state

    def get_trajectory(self):
        return self.planner

    def __replace_joints_in_model_with_map(self):
        joints = {}
        for joint in self.model.joints:
            joints[joint.name] = joint
        del self.model.joints[:]
        self.model.joints = joints

    # def plan_trajectory(self, joint_group, states, samples, duration):
    def plan_trajectory(self, *args, **kwargs):
        joints = []
        if "group" in kwargs:
            joint_group = kwargs["group"]
        if "samples" in kwargs:
            samples = kwargs["samples"]
        if "duration" in kwargs:
            duration = kwargs["duration"]
        if "solver" in kwargs:
            solver = kwargs["solver"]
        else:
            solver = "SCS"
        if "decimals_to_round" in kwargs:
            decimals_to_round = kwargs["decimals_to_round"]
        else:
            decimals_to_round = 3
        if "solver" in kwargs:
            solver = kwargs["solver"]
        else:
            solver = "SCS"
        if "current_state" in kwargs:
            self.update_robot_state(kwargs["current_state"])
        if "goal_state" in kwargs:
            goal_state = kwargs["goal_state"]

        if "states" in kwargs:
            states = kwargs["states"]

        elif "current_state" in kwargs and "goal_state" in kwargs:
            states = {}
            for joint in self.model.joints:
                for joint_in_group in joint_group:
                    if joint_in_group in self.state and joint_in_group in goal_state:
                        states[joint_in_group] = {"start": self.state[joint_in_group]["current_value"], "end": goal_state[joint_in_group]}

                    if joint.name == joint_in_group:
                        joints.append(munchify({
                            "name": joint.name,
                            "states": states[joint_in_group],
                            "limits": joint.limit
                        }))
        self.planner = Planner.TrajectoryOptimizationPlanner(joints=joints, samples=samples, duration=duration,
                                                             solver=solver, solver_class=0, decimals_to_round=decimals_to_round)
        # self.planner.displayProblem()
        self.planner.calculate_trajectory()

    def get_robot_trajectory(self):
        return self.planner.trajectory.get_trajectory()

    def update_robot_state(self, current_state):
        for key, value in self.state.items():
            self.state[key]["current_value"] = current_state[key]

        # print self.state


if __name__ == "__main__":
    robo = Robot(None)

    goal_state = {
        'lbr_iiwa_joint_1': -2.0417782994426674,
        'lbr_iiwa_joint_2': 0.9444594031189716,
        'lbr_iiwa_joint_3': -1.591006403858707,
        'lbr_iiwa_joint_4': -1.9222844444479184,
        'lbr_iiwa_joint_5': 1.572303282659756,
        'lbr_iiwa_joint_6': 1.5741716208788483,
        'lbr_iiwa_joint_7': 1.5716145442929421
    }
    current_state = {
        'lbr_iiwa_joint_1': -0.49197958189616936,
        'lbr_iiwa_joint_2': 1.4223062659337982,
        'lbr_iiwa_joint_3': -1.5688299779644697,
        'lbr_iiwa_joint_4':  -1.3135004031364736,
        'lbr_iiwa_joint_5': 1.5696229411153653,
        'lbr_iiwa_joint_6': 1.5749627479696093,
        'lbr_iiwa_joint_7': 1.5708037563007493,
    }
    states = {
        # 'lbr_iiwa_joint_1': {"start": -0.49, "end": -2.0},
        'lbr_iiwa_joint_1': {"start": -0.49197958189616936, "end": -2.0417782994426674},
        'lbr_iiwa_joint_2': {"start": 1.4223062659337982, "end": 0.9444594031189716},
        'lbr_iiwa_joint_3': {"start": -1.5688299779644697, "end": -1.591006403858707},
        'lbr_iiwa_joint_4': {"start": -1.3135004031364736, "end": -1.9222844444479184},
        'lbr_iiwa_joint_5': {"start": 1.5696229411153653, "end": 1.572303282659756},
        'lbr_iiwa_joint_6': {"start": 1.5749627479696093, "end": 1.5741716208788483},
        'lbr_iiwa_joint_7': {"start": 1.5708037563007493, "end": 1.5716145442929421}
    }

    group1_test = ['lbr_iiwa_joint_1']

    group1 = ['lbr_iiwa_joint_1', 'lbr_iiwa_joint_2', 'lbr_iiwa_joint_3']
    group2 = ['lbr_iiwa_joint_4', 'lbr_iiwa_joint_5', 'lbr_iiwa_joint_6', 'lbr_iiwa_joint_7']
    duration = 6
    samples = 5
    start = time.time()

    # robo.update_robot_state(current_state)
    # robo.plan_trajectory(group=group1_test, current_state=current_state, goal_state=goal_state,
    #                      samples=samples, duration=duration)
    # robo.plan_trajectory(group=group1_test, states=states, samples=samples, duration=duration)
    # joints.plan_trajectory(group1 , samples, duration)
    # print robo.model.joints["lbr_iiwa_joint_5"]
    # print robo.get_robot_trajectory()

    file_path_prefix = '../../config/'

    robot_config_file = file_path_prefix + 'robot_config.yaml'
    robot_yaml = yaml.ConfigParser(robot_config_file)
    robot_config = robot_yaml.get_by_key("robot")
    # print robot_config["joint_configurations"]
    robo.plan_trajectory(group=group1 + group2 + group1 + group2 , current_state=current_state,
                         goal_state=robot_config["joint_configurations"]["home"],
                                              samples=samples, duration=duration)
    end = time.time()
    print("computation time: ", end - start)
