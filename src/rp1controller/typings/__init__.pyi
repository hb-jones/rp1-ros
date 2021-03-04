class Odrive:
    pass
    class system_stats:
        pass
        class usb:
            pass
            rx_cnt: int
            tx_cnt: int
            tx_overrun_cnt: int
        class i2c:
            pass
            addr: int
            addr_match_cnt: int
            rx_cnt: int
            error_cnt: int
        uptime: int
        min_heap_space: int
        min_stack_space_axis0: int
        min_stack_space_axis1: int
        min_stack_space_comms: int
        min_stack_space_usb: int
        min_stack_space_uart: int
        min_stack_space_can: int
        min_stack_space_usb_irq: int
        min_stack_space_startup: int
        stack_usage_axis0: int
        stack_usage_axis1: int
        stack_usage_comms: int
        stack_usage_usb: int
        stack_usage_uart: int
        stack_usage_usb_irq: int
        stack_usage_startup: int
        stack_usage_can: int
    class config:
        pass
        class gpio1_pwm_mapping:
            pass
            endpoint: tuple
            min: float
            max: float
        class gpio2_pwm_mapping:
            pass
            endpoint: tuple
            min: float
            max: float
        class gpio3_pwm_mapping:
            pass
            endpoint: tuple
            min: float
            max: float
        class gpio4_pwm_mapping:
            pass
            endpoint: tuple
            min: float
            max: float
        class gpio3_analog_mapping:
            pass
            endpoint: tuple
            min: float
            max: float
        class gpio4_analog_mapping:
            pass
            endpoint: tuple
            min: float
            max: float
        enable_uart: bool
        uart_baudrate: int
        enable_i2c_instead_of_can: bool
        enable_ascii_protocol_on_usb: bool
        max_regen_current: float
        brake_resistance: float
        dc_bus_undervoltage_trip_level: float
        dc_bus_overvoltage_trip_level: float
        enable_dc_bus_overvoltage_ramp: bool
        dc_bus_overvoltage_ramp_start: float
        dc_bus_overvoltage_ramp_end: float
        dc_max_positive_current: float
        dc_max_negative_current: float
    class axis0(Axis):
        pass
        class config:
            pass
            class calibration_lockin:
                pass
                current: float
                ramp_time: float
                ramp_distance: float
                accel: float
                vel: float
            class sensorless_ramp:
                pass
                current: float
                ramp_time: float
                ramp_distance: float
                accel: float
                vel: float
                finish_distance: float
                finish_on_vel: bool
                finish_on_distance: bool
                finish_on_enc_idx: bool
            class general_lockin:
                pass
                current: float
                ramp_time: float
                ramp_distance: float
                accel: float
                vel: float
                finish_distance: float
                finish_on_vel: bool
                finish_on_distance: bool
                finish_on_enc_idx: bool
            startup_motor_calibration: bool
            startup_encoder_index_search: bool
            startup_encoder_offset_calibration: bool
            startup_closed_loop_control: bool
            startup_sensorless_control: bool
            startup_homing: bool
            enable_step_dir: bool
            step_dir_always_on: bool
            turns_per_step: float
            watchdog_timeout: float
            enable_watchdog: bool
            step_gpio_pin: int
            dir_gpio_pin: int
            can_node_id: int
            can_node_id_extended: bool
            can_heartbeat_rate_ms: int
        class fet_thermistor:
            pass
            class config:
                pass
                temp_limit_lower: float
                temp_limit_upper: float
                enabled: bool
            error: int
            temperature: float
        class motor_thermistor:
            pass
            class config:
                pass
                gpio_pin: int
                poly_coefficient_0: float
                poly_coefficient_1: float
                poly_coefficient_2: float
                poly_coefficient_3: float
                temp_limit_lower: float
                temp_limit_upper: float
                enabled: bool
            error: int
            temperature: float
        class motor:
            pass
            class current_control:
                pass
                p_gain: float
                i_gain: float
                v_current_control_integral_d: float
                v_current_control_integral_q: float
                Ibus: float
                final_v_alpha: float
                final_v_beta: float
                Id_setpoint: float
                Iq_setpoint: float
                Iq_measured: float
                Id_measured: float
                I_measured_report_filter_k: float
                max_allowed_current: float
                overcurrent_trip_level: float
                acim_rotor_flux: float
                async_phase_vel: float
                async_phase_offset: float
            class gate_driver:
                pass
                drv_fault: int
            class timing_log:
                pass
                general: int
                adc_cb_i: int
                adc_cb_dc: int
                meas_r: int
                meas_l: int
                enc_calib: int
                idx_search: int
                foc_voltage: int
                foc_current: int
                spi_start: int
                sample_now: int
                spi_end: int
            class config:
                pass
                pre_calibrated: bool
                pole_pairs: int
                calibration_current: float
                resistance_calib_max_voltage: float
                phase_inductance: float
                phase_resistance: float
                torque_constant: float
                direction: int
                motor_type: int
                current_lim: float
                current_lim_margin: float
                torque_lim: float
                inverter_temp_limit_lower: float
                inverter_temp_limit_upper: float
                requested_current_range: float
                current_control_bandwidth: float
                acim_slip_velocity: float
                acim_gain_min_flux: float
                acim_autoflux_min_Id: float
                acim_autoflux_enable: bool
                acim_autoflux_attack_gain: float
                acim_autoflux_decay_gain: float
            error: int
            armed_state: int
            is_calibrated: bool
            current_meas_phB: float
            current_meas_phC: float
            DC_calib_phB: float
            DC_calib_phC: float
            phase_current_rev_gain: float
            effective_current_lim: float
        class controller:
            pass
            class config:
                pass
                class anticogging:
                    pass
                    index: int
                    pre_calibrated: bool
                    calib_anticogging: bool
                    calib_pos_threshold: float
                    calib_vel_threshold: float
                    cogging_ratio: float
                    anticogging_enabled: bool
                gain_scheduling_width: float
                enable_vel_limit: bool
                enable_current_mode_vel_limit: bool
                enable_gain_scheduling: bool
                enable_overspeed_error: bool
                control_mode: int
                input_mode: int
                pos_gain: float
                vel_gain: float
                vel_integrator_gain: float
                vel_limit: float
                vel_limit_tolerance: float
                vel_ramp_rate: float
                torque_ramp_rate: float
                circular_setpoints: bool
                circular_setpoint_range: float
                homing_speed: float
                inertia: float
                axis_to_mirror: int
                mirror_ratio: float
                load_encoder_axis: int
                input_filter_bandwidth: float
            error: int
            input_pos: float
            input_vel: float
            input_torque: float
            pos_setpoint: float
            vel_setpoint: float
            torque_setpoint: float
            trajectory_done: bool
            vel_integrator_torque: float
            anticogging_valid: bool
            def move_incremental(displacement: float, from_input_pos: bool):
                pass
            def start_anticogging_calibration():
                pass
        class encoder:
            pass
            class config:
                pass
                mode: int
                use_index: bool
                find_idx_on_lockin_only: bool
                abs_spi_cs_gpio_pin: int
                zero_count_on_find_idx: bool
                cpr: int
                offset: int
                pre_calibrated: bool
                offset_float: float
                enable_phase_interpolation: bool
                bandwidth: float
                calib_range: float
                calib_scan_distance: float
                calib_scan_omega: float
                idx_search_unidirectional: bool
                ignore_illegal_hall_state: bool
                sincos_gpio_pin_sin: int
                sincos_gpio_pin_cos: int
            error: int
            is_ready: bool
            index_found: bool
            shadow_count: int
            count_in_cpr: int
            interpolation: float
            phase: float
            pos_estimate: float
            pos_estimate_counts: float
            pos_cpr: float
            pos_cpr_counts: float
            pos_circular: float
            hall_state: int
            vel_estimate: float
            vel_estimate_counts: float
            calib_scan_response: float
            pos_abs: int
            spi_error_rate: float
            def set_linear_count(count: int):
                pass
        class sensorless_estimator:
            pass
            class config:
                pass
                observer_gain: float
                pll_bandwidth: float
                pm_flux_linkage: float
            error: int
            phase: float
            pll_pos: float
            vel_estimate: float
        class trap_traj:
            pass
            class config:
                pass
                vel_limit: float
                accel_limit: float
                decel_limit: float
        class min_endstop:
            pass
            class config:
                pass
                gpio_num: int
                enabled: bool
                offset: float
                is_active_high: bool
                pullup: bool
                debounce_ms: int
            endstop_state: bool
        class max_endstop:
            pass
            class config:
                pass
                gpio_num: int
                enabled: bool
                offset: float
                is_active_high: bool
                pullup: bool
                debounce_ms: int
            endstop_state: bool
        error: int
        step_dir_active: bool
        current_state: int
        requested_state: int
        loop_counter: int
        lockin_state: int
        is_homed: bool
        def watchdog_feed():
            pass
        def clear_errors():
            pass
    class axis1(Axis):
        pass
        class config:
            pass
            class calibration_lockin:
                pass
                current: float
                ramp_time: float
                ramp_distance: float
                accel: float
                vel: float
            class sensorless_ramp:
                pass
                current: float
                ramp_time: float
                ramp_distance: float
                accel: float
                vel: float
                finish_distance: float
                finish_on_vel: bool
                finish_on_distance: bool
                finish_on_enc_idx: bool
            class general_lockin:
                pass
                current: float
                ramp_time: float
                ramp_distance: float
                accel: float
                vel: float
                finish_distance: float
                finish_on_vel: bool
                finish_on_distance: bool
                finish_on_enc_idx: bool
            startup_motor_calibration: bool
            startup_encoder_index_search: bool
            startup_encoder_offset_calibration: bool
            startup_closed_loop_control: bool
            startup_sensorless_control: bool
            startup_homing: bool
            enable_step_dir: bool
            step_dir_always_on: bool
            turns_per_step: float
            watchdog_timeout: float
            enable_watchdog: bool
            step_gpio_pin: int
            dir_gpio_pin: int
            can_node_id: int
            can_node_id_extended: bool
            can_heartbeat_rate_ms: int
        class fet_thermistor:
            pass
            class config:
                pass
                temp_limit_lower: float
                temp_limit_upper: float
                enabled: bool
            error: int
            temperature: float
        class motor_thermistor:
            pass
            class config:
                pass
                gpio_pin: int
                poly_coefficient_0: float
                poly_coefficient_1: float
                poly_coefficient_2: float
                poly_coefficient_3: float
                temp_limit_lower: float
                temp_limit_upper: float
                enabled: bool
            error: int
            temperature: float
        class motor:
            pass
            class current_control:
                pass
                p_gain: float
                i_gain: float
                v_current_control_integral_d: float
                v_current_control_integral_q: float
                Ibus: float
                final_v_alpha: float
                final_v_beta: float
                Id_setpoint: float
                Iq_setpoint: float
                Iq_measured: float
                Id_measured: float
                I_measured_report_filter_k: float
                max_allowed_current: float
                overcurrent_trip_level: float
                acim_rotor_flux: float
                async_phase_vel: float
                async_phase_offset: float
            class gate_driver:
                pass
                drv_fault: int
            class timing_log:
                pass
                general: int
                adc_cb_i: int
                adc_cb_dc: int
                meas_r: int
                meas_l: int
                enc_calib: int
                idx_search: int
                foc_voltage: int
                foc_current: int
                spi_start: int
                sample_now: int
                spi_end: int
            class config:
                pass
                pre_calibrated: bool
                pole_pairs: int
                calibration_current: float
                resistance_calib_max_voltage: float
                phase_inductance: float
                phase_resistance: float
                torque_constant: float
                direction: int
                motor_type: int
                current_lim: float
                current_lim_margin: float
                torque_lim: float
                inverter_temp_limit_lower: float
                inverter_temp_limit_upper: float
                requested_current_range: float
                current_control_bandwidth: float
                acim_slip_velocity: float
                acim_gain_min_flux: float
                acim_autoflux_min_Id: float
                acim_autoflux_enable: bool
                acim_autoflux_attack_gain: float
                acim_autoflux_decay_gain: float
            error: int
            armed_state: int
            is_calibrated: bool
            current_meas_phB: float
            current_meas_phC: float
            DC_calib_phB: float
            DC_calib_phC: float
            phase_current_rev_gain: float
            effective_current_lim: float
        class controller:
            pass
            class config:
                pass
                class anticogging:
                    pass
                    index: int
                    pre_calibrated: bool
                    calib_anticogging: bool
                    calib_pos_threshold: float
                    calib_vel_threshold: float
                    cogging_ratio: float
                    anticogging_enabled: bool
                gain_scheduling_width: float
                enable_vel_limit: bool
                enable_current_mode_vel_limit: bool
                enable_gain_scheduling: bool
                enable_overspeed_error: bool
                control_mode: int
                input_mode: int
                pos_gain: float
                vel_gain: float
                vel_integrator_gain: float
                vel_limit: float
                vel_limit_tolerance: float
                vel_ramp_rate: float
                torque_ramp_rate: float
                circular_setpoints: bool
                circular_setpoint_range: float
                homing_speed: float
                inertia: float
                axis_to_mirror: int
                mirror_ratio: float
                load_encoder_axis: int
                input_filter_bandwidth: float
            error: int
            input_pos: float
            input_vel: float
            input_torque: float
            pos_setpoint: float
            vel_setpoint: float
            torque_setpoint: float
            trajectory_done: bool
            vel_integrator_torque: float
            anticogging_valid: bool
            def move_incremental(displacement: float, from_input_pos: bool):
                pass
            def start_anticogging_calibration():
                pass
        class encoder:
            pass
            class config:
                pass
                mode: int
                use_index: bool
                find_idx_on_lockin_only: bool
                abs_spi_cs_gpio_pin: int
                zero_count_on_find_idx: bool
                cpr: int
                offset: int
                pre_calibrated: bool
                offset_float: float
                enable_phase_interpolation: bool
                bandwidth: float
                calib_range: float
                calib_scan_distance: float
                calib_scan_omega: float
                idx_search_unidirectional: bool
                ignore_illegal_hall_state: bool
                sincos_gpio_pin_sin: int
                sincos_gpio_pin_cos: int
            error: int
            is_ready: bool
            index_found: bool
            shadow_count: int
            count_in_cpr: int
            interpolation: float
            phase: float
            pos_estimate: float
            pos_estimate_counts: float
            pos_cpr: float
            pos_cpr_counts: float
            pos_circular: float
            hall_state: int
            vel_estimate: float
            vel_estimate_counts: float
            calib_scan_response: float
            pos_abs: int
            spi_error_rate: float
            def set_linear_count(count: int):
                pass
        class sensorless_estimator:
            pass
            class config:
                pass
                observer_gain: float
                pll_bandwidth: float
                pm_flux_linkage: float
            error: int
            phase: float
            pll_pos: float
            vel_estimate: float
        class trap_traj:
            pass
            class config:
                pass
                vel_limit: float
                accel_limit: float
                decel_limit: float
        class min_endstop:
            pass
            class config:
                pass
                gpio_num: int
                enabled: bool
                offset: float
                is_active_high: bool
                pullup: bool
                debounce_ms: int
            endstop_state: bool
        class max_endstop:
            pass
            class config:
                pass
                gpio_num: int
                enabled: bool
                offset: float
                is_active_high: bool
                pullup: bool
                debounce_ms: int
            endstop_state: bool
        error: int
        step_dir_active: bool
        current_state: int
        requested_state: int
        loop_counter: int
        lockin_state: int
        is_homed: bool
        def watchdog_feed():
            pass
        def clear_errors():
            pass
    class can:
        pass
        class config:
            pass
            baud_rate: int
            protocol: int
        error: int
        def set_baud_rate(baudRate: int):
            pass
    vbus_voltage: float
    ibus: float
    ibus_report_filter_k: float
    serial_number: int
    hw_version_major: int
    hw_version_minor: int
    hw_version_variant: int
    fw_version_major: int
    fw_version_minor: int
    fw_version_revision: int
    fw_version_unreleased: int
    brake_resistor_armed: bool
    brake_resistor_saturated: bool
    user_config_loaded: bool
    test_property: int
    def test_function(delta: int)->int:
        pass
    def get_oscilloscope_val(index: int)->float:
        pass
    def get_adc_voltage(gpio: int)->float:
        pass
    def save_configuration():
        pass
    def erase_configuration():
        pass
    def reboot():
        pass
    def enter_dfu_mode():
        pass



class Axis:
    pass
    class config:
        pass
        class calibration_lockin:
            pass
            current: float
            ramp_time: float
            ramp_distance: float
            accel: float
            vel: float
        class sensorless_ramp:
            pass
            current: float
            ramp_time: float
            ramp_distance: float
            accel: float
            vel: float
            finish_distance: float
            finish_on_vel: bool
            finish_on_distance: bool
            finish_on_enc_idx: bool
        class general_lockin:
            pass
            current: float
            ramp_time: float
            ramp_distance: float
            accel: float
            vel: float
            finish_distance: float
            finish_on_vel: bool
            finish_on_distance: bool
            finish_on_enc_idx: bool
        startup_motor_calibration: bool
        startup_encoder_index_search: bool
        startup_encoder_offset_calibration: bool
        startup_closed_loop_control: bool
        startup_sensorless_control: bool
        startup_homing: bool
        enable_step_dir: bool
        step_dir_always_on: bool
        turns_per_step: float
        watchdog_timeout: float
        enable_watchdog: bool
        step_gpio_pin: int
        dir_gpio_pin: int
        can_node_id: int
        can_node_id_extended: bool
        can_heartbeat_rate_ms: int
    class fet_thermistor:
        pass
        class config:
            pass
            temp_limit_lower: float
            temp_limit_upper: float
            enabled: bool
        error: int
        temperature: float
    class motor_thermistor:
        pass
        class config:
            pass
            gpio_pin: int
            poly_coefficient_0: float
            poly_coefficient_1: float
            poly_coefficient_2: float
            poly_coefficient_3: float
            temp_limit_lower: float
            temp_limit_upper: float
            enabled: bool
        error: int
        temperature: float
    class motor:
        pass
        class current_control:
            pass
            p_gain: float
            i_gain: float
            v_current_control_integral_d: float
            v_current_control_integral_q: float
            Ibus: float
            final_v_alpha: float
            final_v_beta: float
            Id_setpoint: float
            Iq_setpoint: float
            Iq_measured: float
            Id_measured: float
            I_measured_report_filter_k: float
            max_allowed_current: float
            overcurrent_trip_level: float
            acim_rotor_flux: float
            async_phase_vel: float
            async_phase_offset: float
        class gate_driver:
            pass
            drv_fault: int
        class timing_log:
            pass
            general: int
            adc_cb_i: int
            adc_cb_dc: int
            meas_r: int
            meas_l: int
            enc_calib: int
            idx_search: int
            foc_voltage: int
            foc_current: int
            spi_start: int
            sample_now: int
            spi_end: int
        class config:
            pass
            pre_calibrated: bool
            pole_pairs: int
            calibration_current: float
            resistance_calib_max_voltage: float
            phase_inductance: float
            phase_resistance: float
            torque_constant: float
            direction: int
            motor_type: int
            current_lim: float
            current_lim_margin: float
            torque_lim: float
            inverter_temp_limit_lower: float
            inverter_temp_limit_upper: float
            requested_current_range: float
            current_control_bandwidth: float
            acim_slip_velocity: float
            acim_gain_min_flux: float
            acim_autoflux_min_Id: float
            acim_autoflux_enable: bool
            acim_autoflux_attack_gain: float
            acim_autoflux_decay_gain: float
        error: int
        armed_state: int
        is_calibrated: bool
        current_meas_phB: float
        current_meas_phC: float
        DC_calib_phB: float
        DC_calib_phC: float
        phase_current_rev_gain: float
        effective_current_lim: float
    class controller:
        pass
        class config:
            pass
            class anticogging:
                pass
                index: int
                pre_calibrated: bool
                calib_anticogging: bool
                calib_pos_threshold: float
                calib_vel_threshold: float
                cogging_ratio: float
                anticogging_enabled: bool
            gain_scheduling_width: float
            enable_vel_limit: bool
            enable_current_mode_vel_limit: bool
            enable_gain_scheduling: bool
            enable_overspeed_error: bool
            control_mode: int
            input_mode: int
            pos_gain: float
            vel_gain: float
            vel_integrator_gain: float
            vel_limit: float
            vel_limit_tolerance: float
            vel_ramp_rate: float
            torque_ramp_rate: float
            circular_setpoints: bool
            circular_setpoint_range: float
            homing_speed: float
            inertia: float
            axis_to_mirror: int
            mirror_ratio: float
            load_encoder_axis: int
            input_filter_bandwidth: float
        error: int
        input_vel: float
        input_vel: float
        input_torque: float
        pos_setpoint: float
        input_vel: float
        torque_setpoint: float
        trajectory_done: bool
        vel_integrator_torque: float
        anticogging_valid: bool
        def move_incremental(displacement: float, from_input_pos: bool):
            pass
        def start_anticogging_calibration():
            pass
    class encoder:
        pass
        class config:
            pass
            mode: int
            use_index: bool
            find_idx_on_lockin_only: bool
            abs_spi_cs_gpio_pin: int
            zero_count_on_find_idx: bool
            cpr: int
            offset: int
            pre_calibrated: bool
            offset_float: float
            enable_phase_interpolation: bool
            bandwidth: float
            calib_range: float
            calib_scan_distance: float
            calib_scan_omega: float
            idx_search_unidirectional: bool
            ignore_illegal_hall_state: bool
            sincos_gpio_pin_sin: int
            sincos_gpio_pin_cos: int
        error: int
        is_ready: bool
        index_found: bool
        shadow_count: int
        count_in_cpr: int
        interpolation: float
        phase: float
        pos_estimate: float
        pos_estimate_counts: float
        pos_cpr: float
        pos_cpr_counts: float
        pos_circular: float
        hall_state: int
        vel_estimate: float
        vel_estimate_counts: float
        calib_scan_response: float
        pos_abs: int
        spi_error_rate: float
        def set_linear_count(count: int):
            pass
    class sensorless_estimator:
        pass
        class config:
            pass
            observer_gain: float
            pll_bandwidth: float
            pm_flux_linkage: float
        error: int
        phase: float
        pll_pos: float
        vel_estimate: float
    class trap_traj:
        pass
        class config:
            pass
            vel_limit: float
            accel_limit: float
            decel_limit: float
    class min_endstop:
        pass
        class config:
            pass
            gpio_num: int
            enabled: bool
            offset: float
            is_active_high: bool
            pullup: bool
            debounce_ms: int
        endstop_state: bool
    class max_endstop:
        pass
        class config:
            pass
            gpio_num: int
            enabled: bool
            offset: float
            is_active_high: bool
            pullup: bool
            debounce_ms: int
        endstop_state: bool
    error: int
    step_dir_active: bool
    current_state: int
    requested_state: int
    loop_counter: int
    lockin_state: int
    is_homed: bool
    def watchdog_feed():
        pass
    def clear_errors():
        pass