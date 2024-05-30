module bsg_parallel_in_serial_out_wrapper #(parameter width_p = 16
                            , parameter els_p = 4
                            , parameter hi_to_lo_p = 0
                            ,parameter use_minimal_buffering_p = 1)
    (input clk_i
    ,input reset_i

    // Data Input Channel (Ready and Valid)
    ,input                           valid_i
    ,input  [els_p-1:0][width_p-1:0] data_i
    ,output                          ready_and_o

    // Data Output Channel (Valid then Yumi)
    ,output                          valid_o
    ,output            [width_p-1:0] data_o
    ,input                           yumi_i
    );

    // Instantiate DUT
    bsg_parallel_in_serial_out #(.width_p(width_p)
                                ,.els_p(els_p)
                                ,.hi_to_lo_p(hi_to_lo_p)
                                ,.use_minimal_buffering_p(use_minimal_buffering_p)
    ) piso (.*);

    // Bind Covergroups
    bind bsg_parallel_in_serial_out bsg_parallel_in_serial_out_cov
   #(.els_p(els_p)
    ,.use_minimal_buffering_p(use_minimal_buffering_p)) pc_cov (
        .clk_i(clk_i)
        ,.reset_i(reset_i)
        ,.valid_i(valid_i)
        ,.yumi_i(yumi_i)
        ,.fifo0_ready_and_lo(piso.fifo0_ready_and_lo)
        ,.fifo_v_lo(piso.fifo_v_lo)
        ,.fifo1_ready_and_lo(piso.fifo1_ready_and_lo)
        ,.shift_ctr_r(piso.shift_ctr_r)
    );

    // Dump Waveforms
    initial begin
        $fsdbDumpvars;
    end
    
endmodule