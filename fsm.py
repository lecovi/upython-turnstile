class MachineError(Exception):
    pass

class Machine:    
    valid_states = ['stand_by', 'access_1', 'access_2', 'access_3', 'leave_1', 'leave_2', 'leave_3']
    def __init__(self, initial='stand_by'):
        assert initial in Machine.valid_states
        self.initial = initial
        self.current_state = self.initial
        self.transitions = [
            dict(src='stand_by', trigger='input_on', dst='access_1', before='activate_solenoid'),
            dict(src='access_1', trigger='input_off', dst='stand_by', before='deactivate_solenoid'),
            dict(src='access_1', trigger='output_on', dst='access_2'),
            dict(src='access_2', trigger='output_off', dst='access_1'),
            dict(src='access_2', trigger='input_off', dst='access_3'),
            dict(src='access_3', trigger='output_off', dst='stand_by', after='register_access'),
            dict(src='access_3', trigger='input_off', dst='access_2'),
            dict(src='stand_by', trigger='output_on', dst='leave_1', before='activate_solenoid'),
            dict(src='leave_1', trigger='input_on', dst='leave_2'),
            dict(src='leave_1', trigger='output_off', dst='stand_by', before='deactivate_solenoid'),
            dict(src='leave_2', trigger='output_off', dst='leave_3'),
            dict(src='leave_2', trigger='input_off', dst='leave_1'),
            dict(src='leave_3', trigger='input_off', dst='stand_by', after='register_exit'),
            dict(src='leave_3', trigger='output_on', dst='leave_2'),
        ]
        self.tasks = list()
        self.access_granted = False
        self.exit_granted = True
        self.solenoid = False

    def activate_solenoid(self):
        """
            Verifies if access must be granted, if not will activate solenoid to lock arms.
        """
        if not self.access_granted:
            self.solenoid = True
            print('Solenoide activo')
            return
        print('Permitiendo acceso')
    
    def toggle_solenoid(self):
        """
            Reverse solenoid state.
        """
        self.solenoid = not self.solenoid
        print('Solenoid state set to {}'.format(self.solenoid))

    def deactivate_solenoid(self):
        """
            Set solenoid to false.
        """
        self.solenoid = False
        print('Solenoide desactivado')

    def _get_transition(self, trigger):
        """
            Returns the next state in transitions list or raises a MachineError.
        """
        for transition in self.transitions:
            if transition['trigger'] == trigger and transition['src'] == self.current_state:
                return transition
        raise MachineError('Invalid Transition!')

    def _change_state(self, transition):
        next_state = transition['dst']
        if 'before' in transition.keys():
            func = getattr(self, transition['before'])
            func()
        self.current_state = next_state
        if 'after' in transition.keys():
            func = getattr(self, transition['after'])
            func()

    def change_to(self, trigger):
        transition = self._get_transition(trigger=trigger)
        self._change_state(transition=transition)

    def input_on(self):
        """
            Trigger activated when input sensor is ON.
        """
        try:
            self.change_to(trigger='input_on')
            return self.current_state
        except MachineError:
            print("Registrando anomalía")

    def input_off(self):
        """
            Trigger activated when input sensor is OFF.
        """
        try:
            self.change_to(trigger='input_off')
            return self.current_state
        except MachineError:
            print("Registrando anomalía")

    def output_on(self):
        """
            Trigger activated when output sensor is ON.
        """
        try:
            self.change_to(trigger='output_on')
            return self.current_state
        except MachineError:
            print("Registrando anomalía")

    def output_off(self):
        """
            Trigger activated when output sensor is OFF.
        """
        try:
            self.change_to(trigger='output_off')
            return self.current_state
        except MachineError:
            print("Registrando anomalía")

    def register_access(self):
        """
            Change flag, log and notifies MQTT on access event.
        """
        if self.access_granted:
            self.access_granted = False
            print('Registro de entrada')
        else:
            print('Anomalía de entrada')

    def register_exit(self):
        """
            Change flag, log and notifies MQTT on exit event.
        """
        if self.exit_granted:
            self.exit_granted = False
            print('Registro de salida')
        else:
            print('Anomalía de salida')


class Performance:
    VALID_PERFORMANCE = ['NORMAL', 'FLEXIBLE', 'LIBERADA', 'DESHABILITADO']
    MODE = ['ENTRADA', 'SALIDA', 'VISITAS']

    def __init__(self, name='NORMAL', mode='ENTRADA'):
        self.name = name
        self.mode = mode
        self.input_enabled = None
        self.output_enabled = None

        self._config_arm()

    def _config_arm(self):
        assert self.name in Performance.VALID_PERFORMANCE
        assert self.mode in Performance.MODE

        if self.name in ['NORMAL', 'FLEXIBLE']:
            if self.mode == 'ENTRADA':
                self.input_enabled = False
                self.output_enabled = True
            elif self.mode == 'SALIDA':
                self.input_enabled = True
                self.output_enabled = False
            else:
                self.input_enabled = False
                self.output_enabled = False
        elif self.name == 'LIBERADA':
            self.input_enabled = True
            self.output_enabled = True
        else:
            self.input_enabled = False
            self.output_enabled = False

    def change_to(self, name, mode):
        self.name = name
        self.mode = mode

        self._config_arm()

    def __repr__(self):
        return 'Performance: {}, Mode: {}'.format(self.name, self.mode)


class TurnstileMachine:
    def __init__(self, name): #, performance='NORMAL', mode='ENTRADA'):
        self.name = name
        # self.performance = Performance(name=performance, mode=mode)
        self.access_granted = False
        self.exit_granted = True
        self.solenoid = False
        self.machine = Machine(states=TurnstileMachine.states, initial='stand by')

        self.machine.add_transition(source='stand by', trigger='input_on', dest='access_1', before='input_activate_solenoid')
        self.machine.add_transition(source='access_1', trigger='input_off', dest='stand by', before='deactivate_solenoid')
        self.machine.add_transition(source='access_1', trigger='output_on', dest='access_2')
        self.machine.add_transition(source='access_2', trigger='output_off', dest='access_1')
        self.machine.add_transition(source='access_2', trigger='input_off', dest='access_3')
        self.machine.add_transition(source='access_3', trigger='output_off', dest='stand by', after='register_access')
        self.machine.add_transition(source='access_3', trigger='input_off', dest='access_2')
        self.machine.add_transition(source='stand by', trigger='output_on', dest='leave_1', before='output_activate_solenoid')
        self.machine.add_transition(source='leave_1', trigger='input_on', dest='leave_2')
        self.machine.add_transition(source='leave_1', trigger='output_off', dest='stand by', before='deactivate_solenoid')
        self.machine.add_transition(source='leave_2', trigger='output_off', dest='leave_3')
        self.machine.add_transition(source='leave_2', trigger='input_off', dest='leave_1')
        self.machine.add_transition(source='leave_3', trigger='input_off', dest='stand by', after='register_exit')
        self.machine.add_transition(source='leave_3', trigger='output_on', dest='leave_2')

    def input_activate_solenoid(self):
        if not self.access_granted:
            self.solenoid = True
            print('Activando solenoide!')
    
    def deactivate_solenoid(self):
        self.solenoid = False
        print('Solenoide desactivado')

    def output_activate_solenoid(self):
        if not self.exit_granted:
            self.solenoid = True
            print('Activando solenoide!')

    def register_access(self):
        if self.access_granted:
            self.access_granted = False
            print('Registro de entrada')
        else:
            print('Anomalía de entrada')

    def register_exit(self):
        if self.exit_granted:
            self.exit_granted = False
            print('Registro de salida')
        else:
            print('Anomalía de salida')