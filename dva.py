#!testcase!!phys!
# vim:et:sw=4:ts=4:sts=4:ai
# ------------------------------------------------------------------------------
# DVA Test Script
# Software Download on CAN (Device) Revision 001 Volume No 01
# 5.1.1.8 TesterPresent (0x3E)/SPA
# ------------------------------------------------------------------------------
# Notes :
# ------------------------------------------------------------------------------
import sys
import dva
import array
from dva.define import *
try:
    import _dva
except ImportError:
    import test._dva as _dva
from dva.convert import *
import swdl_helper
import Helper_Functions as helpModule
import TestSeq_EnterProgrammingSession as enterProgSession
import TestSeq_DownloadSBL as downloadSBL

dva.validation_variables.validationScripts = ["validate_can_tp.py", "validate_can_background_diagnostic_server.py","validate_session.py", "validate_swdl_TestSeq_EnterProgrammingSession.py"]
dva.validation_variables.num_of_retries = 3


# implementation of actual test case
def execute_testcase():
    # If test case can be aborted prematurely if some step is not executed correctly
    pre_abort_testcase = True
    bFunc = False

    Failed         = 0x1111
    NotExecuted    = 0x0111
    Passed         = 0x0011
    NotApplicable  = 0x0001
    NotRunned      = 0x0000

    # print some generic test information
    dva.generic.print_test_information()

    test_system = dva.test_system.TestSystem.get_instance()

    communication_peer_ecu = test_system.communication_peer_ecu
    ecu_address = communication_peer_ecu.ecu_info.get_spa_address()
    dva_address = test_system.dva_ecu.ecu_info.get_spa_address()

    if not test_system.communication_peer_ecu.ecu_info.is_bootloader():
        dva.generic.set_not_applicable(dva_address, ecu_address ,\
                                       'The ECU is not a Bootloader ECU, therefore the test is NOT_APPLICABLE')
        return

    busType = BUS_TYPE_CAN

    dva_sw = test_system.dva_ecu.ecu_info.sbl
    if busType== BUS_TYPE_FLEXRAY:
        if dva_sw == None:
            dva_sw = test_system.dva_ecu.ecu_info.pbl
            if dva_sw == None:
                dva.generic.add_testcase_error(ecu_address,dva_address ,\
                                               'ERROR: A SBL or PBL in DVA ECU must be selected when running this test.')
                return

    if test_system.communication_peer_ecu.ecu_info.sbl == None:
        if (busType == BUS_TYPE_IP):
            if dva.generic.get_is_edge_node():
                pass
            else:
                dva.generic.set_not_applicable(dva_address, ecu_address ,\
                                               'The ECU is not a Bootloader ECU with SBL and not an edge node, therefore the test is NOT_APPLICABLE')
                return
        else:
            dva.generic.set_not_applicable(dva_address, ecu_address ,\
                                           'The ECU is not a Bootloader ECU with SBL, therefore the test is NOT_APPLICABLE')
            return

    if test_system.communication_peer_ecu.ecu_info.app == None:
        dva.generic.add_testcase_error(ecu_address,dva_address ,\
                                       'ERROR: An application must be selected when running this test.')
        return

    if test_system.communication_peer_ecu.ecu_info.pbl == None:
        dva.generic.add_testcase_error(ecu_address,dva_address ,\
                                       'ERROR: A PBL must be selected when running this test.')
        return

    '''productionKeyIsStored = False	
	if (dva.generic.get_userquestions_popup_enable()):		
		if (dva.generic.user_question( 'Is Production key stored in Test Object?')):
			productionKeyIsStored = True
		else:
			productionKeyIsStored = False #Production key is not Stored!'''
    
    communication_peer_sw = communication_peer_ecu.ecu_info.app
    sbl_to_be_downloaded = (busType != BUS_TYPE_IP) or (not dva.generic.get_is_edge_node())

    # parse vbf-files
    vbf_file_list_ecu    = communication_peer_ecu.ecu_info.vbf_data
    if sbl_to_be_downloaded and swdl_helper.is_vbf_file_list_empty(vbf_file_list_ecu):
        dva.generic.add_testcase_error(ecu_address,dva_address ,'Error: No SBL file is provided, INADEQUATE_DATA to run the test')
        return

    print("Parsing VBF files")
    res = swdl_helper.parse_swdl_file(vbf_file_list_ecu)
    if res <> '':  #means there was a error and res contains the name of the file that is missing
        dva.generic.add_testcase_error(ecu_address,dva_address ,res)
        return

    if sbl_to_be_downloaded and swdl_helper.check_valid_sbl() == False:
        dva.generic.add_testcase_error(ecu_address,dva_address ,'Error: No SBL file is provided, INADEQUATE_DATA to run the test')
        return

    pincode = ""
    if communication_peer_ecu.ecu_info.pincode.has_key(2):
        pincode = communication_peer_ecu.ecu_info.pincode[2]
    if len(pincode) == 10 or len(pincode) == 64:
        try:
            pin = int(pincode,16)
        except ValueError:
            pin = 0
        if pin == 0:
            dva.generic.add_testcase_error(ecu_address,dva_address ,'Error: 5 or 32 byte security constant is configured as zeroes, but the test is continued anyway!')
    else:
        dva.generic.add_testcase_error(ecu_address,dva_address ,'Error: 5 or 32 byte security constant is not configured, INADEQUATE_DATA to run the test')
		return

    #get DID to read ActiveDiagnosticSession
    data_identifier = 0xF186

    if busType== BUS_TYPE_FLEXRAY:
        Flexraynetworkid = _dva.get_flexraynetworkId()
        if (Flexraynetworkid == 2):
                (first_request_slot_phy, last_request_slot_phy,first_request_slot_func, last_request_slot_func) = test_system.test_system_info.network.data_link_layers["Flexray_Front2"].get_request_slot_range(DIAGNOSTIC_SESSION_DEFAULT)
                (first_response_slot, last_response_slot) = test_system.test_system_info.network.data_link_layers["Flexray_Front2"].get_response_slot_range(DIAGNOSTIC_SESSION_DEFAULT)
                _dva.SETTING_KEY__FLEXRAY_BUS_SETUP_PARAMETERS = test_system.test_system_info.network.data_link_layers["Flexray_Front2"].get_flexray_parameter_setup(DIAGNOSTIC_SESSION_DEFAULT)		    
        elif (Flexraynetworkid == 3):
                (first_request_slot_phy, last_request_slot_phy,first_request_slot_func, last_request_slot_func) = test_system.test_system_info.network.data_link_layers["Flexray_Mid2"].get_request_slot_range(DIAGNOSTIC_SESSION_DEFAULT)
                (first_response_slot, last_response_slot) = test_system.test_system_info.network.data_link_layers["Flexray_Mid2"].get_response_slot_range(DIAGNOSTIC_SESSION_DEFAULT)	    
                _dva.SETTING_KEY__FLEXRAY_BUS_SETUP_PARAMETERS = test_system.test_system_info.network.data_link_layers["Flexray_Mid2"].get_flexray_parameter_setup(DIAGNOSTIC_SESSION_DEFAULT)
        else :
                (first_request_slot_phy, last_request_slot_phy,first_request_slot_func, last_request_slot_func) = test_system.test_system_info.network.data_link_layers["Flexray_Backbone"].get_request_slot_range(DIAGNOSTIC_SESSION_DEFAULT)
                (first_response_slot, last_response_slot) = test_system.test_system_info.network.data_link_layers["Flexray_Backbone"].get_response_slot_range(DIAGNOSTIC_SESSION_DEFAULT)
                _dva.SETTING_KEY__FLEXRAY_BUS_SETUP_PARAMETERS = test_system.test_system_info.network.data_link_layers["Flexray_Backbone"].get_flexray_parameter_setup(DIAGNOSTIC_SESSION_DEFAULT)
    settings = {_dva.SETTING_KEY__ZEROPADTOFRAMESIZE:1,
                _dva.SETTING_KEY__FRAMESIZE:8,
                _dva.SETTING_KEY__N_AR_TIMEOUT:communication_peer_sw.get_N_Ar_Timeout("CAN", DIAGNOSTIC_SESSION_DEFAULT),
                _dva.SETTING_KEY__N_BS_TIMEOUT:communication_peer_sw.get_N_Bs_Timeout("CAN", DIAGNOSTIC_SESSION_DEFAULT),
                _dva.SETTING_KEY__N_CR_TIMEOUT:communication_peer_sw.get_N_Cr_Timeout("CAN", DIAGNOSTIC_SESSION_DEFAULT),
                _dva.SETTING_KEY__SYNCHRONOUS_TRANSMISSION:1,
                _dva.SETTING_KEY__NUMBER_OF_IDENTIFIER_BITS:communication_peer_sw.get_address_format("CAN"),
                _dva.SETTING_CANFD_DATARATE:test_system.test_system_info.network.data_link_layers["CANFD"].canfddatabaudrate,
                _dva.SETTING_CANFD_DATASJW:test_system.test_system_info.network.data_link_layers["CANFD"].canfddatasjw,
                _dva.SETTING_CANFD_DATATSEG1:test_system.test_system_info.network.data_link_layers["CANFD"].canfddatatseg1,
                _dva.SETTING_CANFD_DATATSEG2:test_system.test_system_info.network.data_link_layers["CANFD"].canfddatatseg2,
                _dva.SETTING_CANFD_ARBRATE:test_system.test_system_info.network.data_link_layers["CANFD"].canfdarbbaudrate,
                _dva.SETTING_CANFD_ARBSJW:test_system.test_system_info.network.data_link_layers["CANFD"].canfdarbsjw,
                _dva.SETTING_CANFD_ARBTSEG1:test_system.test_system_info.network.data_link_layers["CANFD"].canfdarbtseg1,
                _dva.SETTING_CANFD_ARBTSEG2:test_system.test_system_info.network.data_link_layers["CANFD"].canfdarbtseg2,
                _dva.SETTING_CANFD_FRAMESIZE:test_system.test_system_info.network.data_link_layers["CANFD"].canfdframesize,
                _dva.SETTING_CANNM_FRAME_ENABLE:dva.generic.get_cdb_item("can_nm_frame_enable"),
                _dva.SETTING_CANNM_FRAME_PERIOD:dva.generic.get_cdb_item("can_nm_frame_period"),
                _dva.SETTING_CANID_RX:dva.generic.get_cdb_item("CANidRX"),
                _dva.SETTING_CANID_TX:dva.generic.get_cdb_item("CANidTX"),
                _dva.SETTING_CANFD_BRS_BIT:dva.generic.get_cdb_item("CANFDBRSBitEnable")}

    # starting communication
    if not _dva.start_communication(settings, ecu_address):
        print("ERROR: Communication error!")
        return

    _dva.add_signal(dva_address,ecu_address,SIG_ID__SOFTWARE_TYPE,SOFTWARE_APPLICATION)

    if busType == BUS_TYPE_LIN:
        request = array.array('B',[0x3E, 0x80])
        _dva.send_functional_c_pdu(request, settings)

        #LIN 2.2A standard says to wait at least 100ms after wakeup. this code waits twice that time to guarantee the 100ms, plus that
        #the time is not critical as long as it is longer than 100ms and less than about 3 seconds ( sleep timeout )
        WAKEUP_TIME = 200
        dva.generic.delay(WAKEUP_TIME)

    _dva.activate_tester_present(dva.generic.get_tester_present_periodicity())
    communication_peer_sw = communication_peer_ecu.ecu_info.app
    current_session = dva.define.DIAGNOSTIC_SESSION_DEFAULT
    SWDL_Part_one = True
    if not helpModule.GenericSWDLValidation_BeforeDownlaod(ecu_address,dva_address,SWDL_Part_one):
        dva.generic.add_testcase_error(ecu_address,dva_address , "SDDB ERROR: As Mandatory SDDB Parameters are missing, Unable to Start the Test case.")
        return
    result = enterProgSession.execute(dva_sw,communication_peer_ecu,dva_address,busType)
    if not result['Result']:
        return

    communication_peer_sw = communication_peer_ecu.ecu_info.pbl
    sw_type = SOFTWARE_PBL

    if sbl_to_be_downloaded:
        if not downloadSBL.execute(dva_address,communication_peer_ecu,busType,False,True,False,
					                       result['P1'],result['P2'],result['Q1'],result['Q2']):
            pass
            #return

    # the actual test case starts here
    _session_layer = dva.session_layer.Iso14229Session()

    diag_session_handler = swdl_helper.diag_session_handler(dva_sw,communication_peer_ecu,_session_layer,\
                                                            dva_address,busType)

    #Step 1
    service = 0x22
    step = 1
    did_length = 1
    expected_session = DIAGNOSTIC_SESSION_PROGRAMMING
    v_resp = True
    v_data = [ 0x62, 0xF1, 0x86, 0x02]
    result = helpModule.ReadDataByIdentifier(dva_address, ecu_address, communication_peer_sw, expected_session, _session_layer, data_identifier, did_length, bFunc, busType, v_resp, v_data)
    errorCode = result['valid']
    if errorCode == timeInvalidParams:
        helpModule.ProcessErrorCode(dva_address, ecu_address, errorCode, step)
        return
    if errorCode == responseNotExpected:
        helpModule.ProcessErrorExpectedResponse(dva_address, ecu_address, v_data, step)
    else:
        helpModule.ProcessErrorCode(dva_address, ecu_address, errorCode, step)

    #Step 2
    step=2
    posRespSupress = False
    current_session = dva.define.DIAGNOSTIC_SESSION_PROGRAMMING
    new_session = dva.define.DIAGNOSTIC_SESSION_PROGRAMMING
    result = helpModule.TesterPresent(communication_peer_sw, current_session, posRespSupress, _session_layer, dva_address, ecu_address, bFunc, busType)
    errorCode = result['valid']
    if errorCode == timeInvalidParams:
        helpModule.ProcessErrorCode(dva_address, ecu_address, errorCode, step)
        return
    helpModule.ProcessErrorCode(dva_address, ecu_address, errorCode, step)

    #Step 3
    step = 3
    posRespSupress = True
    current_session = dva.define.DIAGNOSTIC_SESSION_PROGRAMMING
    new_session = dva.define.DIAGNOSTIC_SESSION_PROGRAMMING
    result = helpModule.TesterPresent(communication_peer_sw, current_session, posRespSupress, _session_layer, dva_address, ecu_address, bFunc, busType)
    errorCode = result['valid']
    if errorCode == timeInvalidParams:
        helpModule.ProcessErrorCode(dva_address, ecu_address, errorCode, step)
        return
    helpModule.ProcessErrorCode(dva_address, ecu_address, errorCode, step)

    #Step 4
    posRespSupress = True
    current_session = dva.define.DIAGNOSTIC_SESSION_PROGRAMMING
    new_session = dva.define.DIAGNOSTIC_SESSION_PROGRAMMING

    result = helpModule.RoutineControl_ActivateSecondaryBootloader(communication_peer_sw,_session_layer,communication_peer_ecu,dva_address, bFunc, busType)
    errorCode  = result['valid']
    if errorCode == timeInvalidParams:
        helpModule.ProcessErrorCode(dva_address, ecu_address, errorCode, step)
        return
    if (errorCode == [0x7F,0x31,0x33] and BUS_TYPE_IP == busType):      #Nrip Transfer Present (10220962): Try to Unlock ECU, when Activation got failed...
	    # Request Key
	    service = 0x27
	    step = 4.1
	    posRespSupress = False
	    current_session = dva.define.DIAGNOSTIC_SESSION_PROGRAMMING
	    subFunc = 0x01
	    securityAccessDataRecord = []
        pincode = helpModule.getSecGenPIN(subFunc)
        intGen = helpModule.getSecGenerationUsingPIN(pincode)
        if intGen == 2:
            mydll = helpModule.getSecGen2DLLObj(pincode, subFunc)
            dva.generic.delay(5000)
	        result = helpModule.SecurityAccess_RequestSeed(communication_peer_sw,current_session,subFunc, securityAccessDataRecord, posRespSupress,_session_layer,dva_address, ecu_address, bFunc,False,mydll)
        else:
            result = helpModule.SecurityAccess_RequestSeed(communication_peer_sw,current_session,subFunc, securityAccessDataRecord, posRespSupress,_session_layer,dva_address, ecu_address, bFunc)
															   
	    errorCode = result['valid']
	    if errorCode == timeInvalidParams:
		    helpModule.ProcessErrorCode(dva_address, ecu_address, errorCode, step)
		    return
	    seed = [0x00, 0x00, 0x00]
	    helpModule.ProcessErrorCode(dva_address, ecu_address, errorCode,step)
	    if intGen == 1  and errorCode == ISO14229_NR_positiveResponse:
		    seed = result['response'][2:5]		  
	    
	
	    #Continue even if the pincode is not valid	
	    #Send Key
	    service = 0x27
	    step = 4.2
	    posRespSupress = False
	    current_session = dva.define.DIAGNOSTIC_SESSION_PROGRAMMING
	    subFunc = 0x02
		#bFunc = False
        securityKey = 0
        if intGen == 2:
            result = helpModule.SecurityAccess_SendKey(communication_peer_sw, current_session, subFunc, securityKey, posRespSupress,_session_layer, dva_address, ecu_address, bFunc,mydll)
        else:
            response = helpModule.ComputeKey(communication_peer_ecu, seed)
	        if response['valid'] == ISO14229_NR_positiveResponse:
		        securityKey = response['response']
	        result = helpModule.SecurityAccess_SendKey(communication_peer_sw,current_session,subFunc, securityKey, posRespSupress,_session_layer,dva_address, ecu_address, bFunc)
	    errorCode = result['valid']
	    if errorCode == timeInvalidParams:
		    helpModule.ProcessErrorCode(dva_address, ecu_address, errorCode, step)
		    return
	    helpModule.ProcessErrorCode(dva_address, ecu_address, errorCode,step)
															   
	    
		
		#Activate SBL
	    posRespSupress = True	    
	    current_session = dva.define.DIAGNOSTIC_SESSION_PROGRAMMING
	    new_session = dva.define.DIAGNOSTIC_SESSION_PROGRAMMING
	    result = helpModule.RoutineControl_ActivateSecondaryBootloader(communication_peer_sw,_session_layer,communication_peer_ecu,dva_address, bFunc, busType)
	    errorCode  = result['valid']
	    if errorCode == timeInvalidParams:
		    helpModule.ProcessErrorCode(dva_address, ecu_address, errorCode, step)
		    return
	    if errorCode == False:
		    pass
	    
	    else:
		    if sbl_to_be_downloaded:
			    communication_peer_sw = communication_peer_ecu.ecu_info.sbl
			    _dva.add_signal(dva_address,ecu_address,SIG_ID__SOFTWARE_TYPE, SOFTWARE_SBL)
        #pass
        #dva.generic.add_testcase_debug_error(dva_address, ecu_address, "ERROR: Failed to Activate SBL", 4)
    else:
        if sbl_to_be_downloaded:
            communication_peer_sw = communication_peer_ecu.ecu_info.sbl
            _dva.add_signal(dva_address,ecu_address,SIG_ID__SOFTWARE_TYPE, SOFTWARE_SBL)

    #Step 5
    step = 5
    posRespSupress = False
    current_session = dva.define.DIAGNOSTIC_SESSION_PROGRAMMING
    new_session = dva.define.DIAGNOSTIC_SESSION_PROGRAMMING
    result = helpModule.TesterPresent(communication_peer_sw, current_session, posRespSupress, _session_layer, dva_address, ecu_address, bFunc, busType)
    errorCode = result['valid']
    if errorCode == timeInvalidParams:
        helpModule.ProcessErrorCode(dva_address, ecu_address, errorCode, step)
        return
    helpModule.ProcessErrorCode(dva_address, ecu_address, errorCode, step)

    #Step 6
    step = 6
    posRespSupress = True
    current_session = dva.define.DIAGNOSTIC_SESSION_PROGRAMMING
    new_session = dva.define.DIAGNOSTIC_SESSION_PROGRAMMING
    result = helpModule.TesterPresent(communication_peer_sw, current_session, posRespSupress, _session_layer, dva_address, ecu_address, bFunc, busType)
    errorCode = result['valid']
    if errorCode == timeInvalidParams:
        helpModule.ProcessErrorCode(dva_address, ecu_address, errorCode, step)
        return
    helpModule.ProcessErrorCode(dva_address, ecu_address, errorCode, step)

    # Step 7
    service = 0x22
    step = 7
    did_length = 1
    expected_session = DIAGNOSTIC_SESSION_PROGRAMMING
    v_resp = True
    v_data = [ 0x62, 0xF1, 0x86, 0x02]
    result = helpModule.ReadDataByIdentifier(dva_address, ecu_address, communication_peer_sw, expected_session, _session_layer, data_identifier, did_length, bFunc, busType, v_resp, v_data)
    errorCode = result['valid']
    if errorCode == timeInvalidParams:
        helpModule.ProcessErrorCode(dva_address, ecu_address, errorCode, step)
        return
    if errorCode == responseNotExpected:
        helpModule.ProcessErrorExpectedResponse(dva_address, ecu_address, v_data, step)
    else:
        helpModule.ProcessErrorCode(dva_address, ecu_address, errorCode, step)

    _dva.deactivate_tester_present()
    #vod646if busType == BUS_TYPE_CAN:#Vod-132
		#vod646_dva.deactivate_cannm_frame()
    # >>> testcase end >>>
    _dva.stop_communication()

# execute testcase
dva.generic.RunTestCase(execute_testcase)