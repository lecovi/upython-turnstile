from transitions import Machine


class Performance():
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


class TurnstileMachine():
    states = ['stand by', 'access_1', 'access_2', 'access_3', 'leave_1', 'leave_2', 'leave_3']
    
    def __init__(self, name, performance='NORMAL', mode='ENTRADA'):
        self.name = name
        self.performance = Performance(name=performance, mode=mode)
        self.access_granted = False
        self.exit_granted = True
        self.solenoid = False
        self.machine = Machine(model=self, states=TurnstileMachine.states, initial='stand by')

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