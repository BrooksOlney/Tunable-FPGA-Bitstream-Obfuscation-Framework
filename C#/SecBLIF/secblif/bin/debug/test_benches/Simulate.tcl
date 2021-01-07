
foreach source [glob  *v] {
    set_property source_mgmt_mode None [current_project]
    set last [string last "/" $source]
    set filename [string range $source $last+1 end-2]

    set_property top $filename [get_filesets sim_1]
    set_property top_lib xil_defaultlib [get_filesets sim_1]
    update_compile_order -fileset sim_1

    launch_simulation
    run 1s
    close_sim
}