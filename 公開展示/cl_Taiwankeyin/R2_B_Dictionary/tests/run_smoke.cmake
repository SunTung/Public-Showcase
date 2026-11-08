# Deterministic test fixture cleanup is separate from production no-overwrite safety.
file(REMOVE "${DEST}" "${DEST}.partial")
execute_process(COMMAND "${IMPORTER}" "${SOURCE}" "${DEST}"
 RESULT_VARIABLE status OUTPUT_VARIABLE log ERROR_VARIABLE error)
message(STATUS "${log}")
if(NOT status EQUAL 0)
 message(FATAL_ERROR "R2-B importer smoke failure: ${error}")
endif()
