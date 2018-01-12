import numpy as np
import logging
import collections


class ProblemModelling:
    def __init__(self):
        self.duration = -1
        self.samples = -1
        self.no_of_joints = -1
        self.decimals_to_round = -1
        self.joints = {}
        self.cost_matrix_P = []
        self.cost_matrix_q = []
        self.constraints_matrix = []
        self.velocity_lower_limits = []
        self.velocity_upper_limits = []
        self.joints_lower_limits = []
        self.joints_upper_limits = []
        self.constraints_lower_limits = []
        self.constraints_upper_limits = []
        self.start_and_goal_matrix = []
        self.start_and_goal_limits = []
        self.velocity_upper_limits = []
        self.initial_guess = []
        self.collision_constraints = None

        main_logger_name = "Trajectory_Planner"
        # verbose = "DEBUG"
        verbose = False
        self.logger = logging.getLogger(main_logger_name)
        self.setup_logger(main_logger_name, verbose)

    def init(self, joints, no_of_samples, duration, decimals_to_round=5):
        self.samples = no_of_samples
        self.duration = duration
        self.no_of_joints = len(joints)
        self.joints = joints
        self.decimals_to_round = decimals_to_round
        if "collision_constraints" in self.joints:
            self.collision_constraints = self.joints["collision_constraints"]
        self.fill_cost_matrix()
        # self.fill_velocity_matrix()
        self.fill_constraints()
        self.fill_start_and_goal_matrix()
        self.fill_velocity_limits()

        main_logger_name = "Trajectory_Planner"
        # verbose = "DEBUG"
        verbose = False
        self.logger = logging.getLogger(main_logger_name)
        self.setup_logger(main_logger_name, verbose)

    def fill_cost_matrix(self):

        shape = self.samples * self.no_of_joints
        self.cost_matrix_P = np.zeros((shape, shape))
        i, j = np.indices(self.cost_matrix_P.shape)
        # np.fill_diagonal(A, [1] * param_a + [2] * (shape - 2 * param_a) + [1] * param_a)
        np.fill_diagonal(self.cost_matrix_P,
                         [1] * self.no_of_joints + [2] * (shape - 2 * self.no_of_joints) + [1] * self.no_of_joints)

        self.cost_matrix_P[i == j - self.no_of_joints] = -2.0
        self.cost_matrix_q = np.zeros(shape)
        # self.cost_matrix_P = 2.0 * self.cost_matrix_P + 1e-08 * np.eye(self.cost_matrix_P.shape[1])

        # Make symmetric and not indefinite
        self.cost_matrix_P = (self.cost_matrix_P + self.cost_matrix_P.T) + 1e-08 * np.eye(self.cost_matrix_P.shape[1])

    def fill_start_and_goal_matrix(self):
        # shape = self.samples * self.no_of_joints
        # self.start_and_goal_matrix = np.zeros((2 * self.no_of_joints, shape))
        # print self.start_and_goal_matrix
        #
        # np.fill_diagonal(self.start_and_goal_matrix, [1] * self.no_of_joints +  [0] * self.no_of_joints)
        # i, j = np.indices(self.start_and_goal_matrix.shape)
        #
        # # self.start_and_goal_matrix[i == j + self.no_of_joints] =  [1] * self.no_of_joints +  [0] * self.no_of_joints
        # self.start_and_goal_matrix[i == j - (self.samples + self.no_of_joints)] = [0] * self.no_of_joints + [1] * self.no_of_joints
        #
        # # np.fill_diagonal(self.start_and_goal_matrix,
        # #                  [1] * self.no_of_joints + [0] * (shape - 2 * self.no_of_joints) + [1] * self.no_of_joints)

        shape = self.samples * self.no_of_joints
        self.start_and_goal_matrix = np.zeros((2 * self.no_of_joints, shape))
        i, j = np.indices(self.start_and_goal_matrix.shape)

        # start = np.zeros((2 * self.no_of_joints, shape))
        # end = np.zeros((2 * self.no_of_joints, shape))
        # np.fill_diagonal(start, [1] * self.no_of_joints + [0] * self.no_of_joints)
        # np.fill_diagonal(end, [1] * self.no_of_joints + [0] * self.no_of_joints)
        # self.start_and_goal_matrix = start + np.fliplr(end)
        self.start_and_goal_matrix[i == j] = [1] * self.no_of_joints + [0] * self.no_of_joints
        self.start_and_goal_matrix[i == j - (shape - 2* self.no_of_joints) ] = [0] * self.no_of_joints + [1] * self.no_of_joints

    def fill_velocity_matrix(self):

        self.constraints_matrix = np.zeros((self.no_of_joints * self.samples, self.samples * self.no_of_joints))
        np.fill_diagonal(self.constraints_matrix, -1.0)
        i, j = np.indices(self.constraints_matrix.shape)
        self.constraints_matrix[i == j - self.no_of_joints] = -1.0

        # to slice zero last row
        self.constraints_matrix.resize(self.constraints_matrix.shape[0] - self.no_of_joints, self.constraints_matrix.shape[1])

    def fill_velocity_limits(self):
        start_and_goal_lower_limits = []
        start_and_goal_upper_limits = []

        for joint in self.joints:
            if type(joint) is dict:
                max_vel = self.joints[joint]["limit"]["velocity"]
                min_vel = -self.joints[joint]["limit"]["velocity"]
                joint_lower_limit = self.joints[joint]["limit"]["lower"]
                joint_upper_limit = self.joints[joint]["limit"]["upper"]
            else:
                max_vel = self.joints[joint].limit.velocity
                min_vel = -self.joints[joint].limit.velocity
                joint_lower_limit = self.joints[joint].limit.lower
                joint_upper_limit = self.joints[joint].limit.upper


            # min_vel = min_vel * self.duration / float(self.samples - 1)
            # max_vel = max_vel * self.duration / float(self.samples - 1)

            min_vel_ = min(min_vel * self.duration / float(self.samples - 1), 2 * joint_lower_limit)
            max_vel_ = max(max_vel * self.duration / float(self.samples - 1), 2 * joint_upper_limit)

            min_vel = min_vel_ if min_vel < min_vel_ else min_vel
            max_vel = max_vel_ if max_vel_ < max_vel else max_vel

            self.velocity_lower_limits.append(np.full((1, self.samples - 1), min_vel))
            self.velocity_upper_limits.append(np.full((1, self.samples - 1), max_vel))
            self.joints_lower_limits.append(joint_lower_limit)
            self.joints_upper_limits.append(joint_upper_limit)
            start_state = np.round(self.joints[joint]["states"]["start"], self.decimals_to_round)
            end_state = np.round(self.joints[joint]["states"]["end"], self.decimals_to_round)
            start_and_goal_lower_limits.append(np.round(start_state, self.decimals_to_round))
            start_and_goal_upper_limits.append(np.round(end_state, self.decimals_to_round))
            self.initial_guess.append(self.interpolate(start_state, end_state))

        self.joints_lower_limits = np.hstack([self.joints_lower_limits] * self.samples).reshape(
            (1, len(self.joints_lower_limits) * self.samples))
        self.joints_upper_limits = np.hstack([self.joints_upper_limits] * self.samples).reshape(
            (1, len(self.joints_upper_limits) * self.samples))

        self.velocity_lower_limits = np.hstack(self.velocity_lower_limits)
        self.velocity_upper_limits = np.hstack(self.velocity_upper_limits)

        self.constraints_lower_limits = np.hstack([self.velocity_lower_limits, self.joints_lower_limits])
        self.constraints_upper_limits = np.hstack([self.velocity_upper_limits, self.joints_upper_limits])
        # print self.constraints_lower_limits
        # print self.constraints_upper_limits
        # print np.full((1, self.samples - 2), 0).flatten()
        # self.start_and_goal_limits = np.hstack(
        #     [start_and_goal_lower_limits, np.full((1, (self.samples - 2) * self.no_of_joints), 0).flatten(),
        #      start_and_goal_upper_limits])
        self.start_and_goal_limits = np.hstack(
            [start_and_goal_lower_limits, start_and_goal_upper_limits])
        self.initial_guess = (np.asarray(self.initial_guess).T).flatten()
        # print self.initial_guess

    def get_collision_matrix(self):
        collision_matrix = []

        row = self.samples * self.no_of_joints
        column = self.samples * (self.no_of_joints + 1)
        collision_matrix = np.zeros((row, column))
        i, j = np.indices(collision_matrix.shape)
        # np.fill_diagonal(A, [1] * param_a + [2] * (shape - 2 * param_a) + [1] * param_a)
        # np.fill_diagonal(collision_matrix,
        #                  [1] * self.no_of_joints + [2] * (row - 2 * self.no_of_joints) + [1] * self.no_of_joints)
        #
        # collision_matrix[i == j - self.no_of_joints] = -2.0
        # self.cost_matrix_P = 2.0 * self.cost_matrix_P + 1e-08 * np.eye(self.cost_matrix_P.shape[1])

        # collision_matrix[::3,:1:] = -1
        # collision_matrix[1:1:3,:2:] = -2

        collision_matrix[i == j - self.samples] = 1.0
        temp = [1] * self.no_of_joints + [0] * (row - self.samples)
        print row, column
        print self.samples, self.no_of_joints
        print temp
        collision_matrix[i == j] = 2
        # collision_matrix[i == j - self.no_of_joints] = [1] * self.samples + [0] * self.samples
        # collision_matrix[i == j + (self.no_of_joints + 1)] = [1] * (self.no_of_joints * self.samples - self.samples)


        # collision_matrix[i == j + (self.samples)] = [-1] * (self.samples)
        collision_matrix[i == j + (self.samples)] = 3

        print collision_matrix



        return collision_matrix

    def get_velocity_matrix(self):

        velocity_matrix = np.zeros((self.no_of_joints * self.samples, self.samples * self.no_of_joints))
        np.fill_diagonal(velocity_matrix, -1.0)
        i, j = np.indices(velocity_matrix.shape)
        velocity_matrix[i == j - self.no_of_joints] = -1.0

        # to slice zero last row
        velocity_matrix.resize(velocity_matrix.shape[0] - self.no_of_joints, velocity_matrix.shape[1])

        return velocity_matrix

    def get_joints_matrix(self):

        joints_matrix = np.eye(self.samples * self.no_of_joints)
        return joints_matrix

    def fill_constraints(self):
        self.velocity_matrix = self.get_velocity_matrix()
        self.joints_matrix = self.get_joints_matrix()
        # self.constraints_matrix = np.vstack([self.velocity_matrix, self.joints_matrix])
        self.constraints_matrix.append(self.velocity_matrix)
        self.constraints_matrix.append(self.joints_matrix)
        self.constraints_matrix = np.vstack(self.constraints_matrix)

        collision_constraints = []
        # # print self.joints["lbr_iiwa_joint_5"]["collision_constraints"]
        # # if self.collision_constraints is not None:
        # for joint_name, joint in self.joints.items():
        #     # print joint_name, joint
        #     # for constraints in joint.collision_constraints:
        #         # print joint.collision_constraints.limits
        #     if type(self.collision_constraints) is dict:
        #         # lower_limit = self.collision_constraints["limits"]["lower"] - \
        #         #               self.collision_constraints["initial_signed_distance"]
        #         initial_signed_distance = joint["collision_constraints"]["initial_signed_distance"]
        #         lower_limit = joint["collision_constraints"]["limits"]["lower"]
        #         upper_limit = joint["collision_constraints"]["limits"]["upper"]
        #         normal = joint["collision_constraints"]["normal"]
        #         jacobian = joint["collision_constraints"]["jacobian"]
        #         max_vel = self.joints[joint]["limit"]["velocity"]
        #
        #     else:
        #         # lower_limit = self.collision_constraints.limits.lower - \
        #         #               self.collision_constraints.initial_signed_distance
        #         initial_signed_distance = joint.collision_constraints.initial_signed_distance
        #         lower_limit = joint.collision_constraints.limits.lower
        #         upper_limit = joint.collision_constraints.limits.upper
        #         normal = joint.collision_constraints.normal
        #         jacobian = joint.collision_constraints.jacobian
        #         max_vel = joint.limit.velocity
        #
        #         if type(normal) is list or tuple:
        #             normal = np.asarray(normal)
        #         if type(jacobian) is list or tuple:
        #             jacobian = np.asarray(jacobian)
        #         normal_times_jacobian = np.matmul(normal.T, jacobian)
        #
        #         # print joint_name, normal_times_jacobian
        #
        # # collision_matrix = self.get_collision_matrix()

    def interpolate(self, start, end, samples=None):
        if samples is None:
            samples = self.samples
        data = []
        step_size = (end - start) / (samples - 1)
        intermediate = start
        for i in range(samples):
            data.append(intermediate)
            intermediate += step_size
        return np.round(data, self.decimals_to_round)

    def __diagonal_block_mat_slicing(self, matrix):
        shape = matrix[0].shape
        length = len(matrix)
        length_range = range(length)
        out = np.zeros((length, shape[0], length, shape[1]), dtype=int)
        out[length_range, :, length_range, :] = matrix
        return out.reshape(np.asarray(shape) * length)

    def setup_logger(self, main_logger_name, verbose=False, log_file=False):

        # creating a formatter
        formatter = logging.Formatter('-%(asctime)s - %(name)s - %(levelname)-8s: %(message)s')

        # create console handler with a debug log level
        log_console_handler = logging.StreamHandler()
        if log_file:
            # create file handler which logs info messages
            logger_file_handler = logging.FileHandler(main_logger_name + '.log', 'w', 'utf-8')
            logger_file_handler.setLevel(logging.INFO)
            # setting handler format
            logger_file_handler.setFormatter(formatter)
            # add the file logging handlers to the logger
            self.logger.addHandler(logger_file_handler)

        if verbose == "WARN":
            self.logger.setLevel(logging.WARN)
            log_console_handler.setLevel(logging.WARN)

        elif verbose == "INFO" or verbose is True:
            self.logger.setLevel(logging.INFO)
            log_console_handler.setLevel(logging.INFO)

        elif verbose == "DEBUG":
            self.logger.setLevel(logging.DEBUG)
            log_console_handler.setLevel(logging.DEBUG)

        # setting console handler format
        log_console_handler.setFormatter(formatter)
        # add the handlers to the logger
        self.logger.addHandler(log_console_handler)



