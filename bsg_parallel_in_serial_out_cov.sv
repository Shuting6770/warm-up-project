`include "bsg_defines.sv"

module bsg_parallel_in_serial_out_cov
    #(parameter els_p = "inv"
    ,parameter use_minimal_buffering_p = 0
    ,localparam clog2els_lp = $clog2(els_p))

    (input clk_i
    ,input reset_i
    
    // interface signals
    ,input valid_i
    ,input yumi_i
    
    //internal regs
    ,input fifo0_ready_and_lo
    ,input fifo_v_lo
    ,input fif01_ready_and_lo
    ,input [clog2els_lp-1:0] shift_ctr_r
    );

    // reset
    covergroup cg_reset @(negedge clk_i);
        coverpoint reset_i;
    endgroup

    // Partitioning covergroup into smaller ones
    //empty: fifo_v_lo == 0 
    // 不可能出现的情况：如果是bsg_one_fifo, 则不可能出现ready_and_o==0
    //                 如果是bsg_two_fifo, 则不可能出现ready_and_o==0
    covergroup cg_empty @ (negedge clk_i iff ~reset_i & ~fifo_v_lo);
        cp_valid: coverpoint valid_i;
        // cannot deque when empty 因为是yumi所以必须先valid_o==1
        cp_yumi:  coverpoint yumi_i {illegal_bins ig = {1};}
        // if empty fifo always ready to input data
        cp_fral0: coverpoint fifo0_ready_and_lo {illegal_bins ig = {0}};
        cp_fral1: coverpoint fifo1_ready_and_lo {illegal_bins ig = {0}};
        cp_scr: coverpoint shift_ctr_r;
    endgroup

    //non-empty: fifo_v_lo == 1
    // 不可能出现的情况：如果是bsg_one_fifo, 则不可能出现ready_and_o==1
    //                 如果是bsg_two_fifo, ready_and_o==0 or 1
    covergroup cg_nonempty @ (negedge clk_i iff ~reset_i & fifo_v_lo);
        cp_valid: coverpoint valid_i;
        cp_yumi:  coverpoint yumi_i;
        // if nonempty bsg_one_fifo is full, bsg_two_fifo can be full/normal
        // if full ready_and_o==0
        cp_fral0: coverpoint fifo0_ready_and_lo;
        cp_fral1: coverpoint fifo1_ready_and_lo;
        cp_scr: coverpoint shift_ctr_r;

        cross_all: coverpoint cp_valid, cp_yumi, cp_fral0, cp_fral1, cp_scr {
            // if bsg_one_fifo, nonempty==full
            illegal_bins ig0 = cross_all with (cp_fral0 && use_minimal_buffering_p);
            // if data in fifo1 has not been all trans, not ready!
            illegal_bins ig1 = cross_all with (shift_ctr_r<=els_p-2 && cp_fral1)
        }
    endgroup

    // create cover groups
    cg_reset cov_reset = new;
    cg_empty cov_empty = new;
    cg_nonempty cov_nonempty = new;

    // print coverages when simulation is done
    final 
    begin
        $display("");
        $display("Instance: %m");
        $display("---------------------- Functional Coverage Results ----------------------");
        $display("Reset       functional coverage is %f%%", cov_reset.get_coverage());
        $display("PISO empty  functional coverage is %f%%", cov_empty.cross_all.get_coverage());
        $display("PISO nonempty   functional coverage is %f%%", cov_nonempty.cross_all.get_coverage());
        $display("-------------------------------------------------------------------------");
        $display("");
    end

endmodule