# Import python libraries
import math
import time
import random

# Import cocotb libraries
import cocotb
from cocotb.clock import Clock, Timer
from cocotb.triggers import RisingEdge, FallingEdge, Timer


# Data width, matching width_p parameter in DUT
WIDTH_P = 16
ELS_P = 4

# Testbench iterations
ITERATION = 1000

# Flow control random seed
# Use different seeds on input and output sides for more randomness
CTRL_INPUT_SEED  = 1
CTRL_OUTPUT_SEED = 2

# Testbench clock period
CLK_PERIOD = 10


async def input_side_testbench(dut, seed):
    """Handle input traffic"""

    # Create local random generator for data generation
    data_random = random.Random()
    data_random.seed(seed)

    # Create control random generator for flow control
    control_random = random.Random()
    control_random.seed(CTRL_INPUT_SEED)

    # Initialize DUT interface values
    dut.valid_i.value = 0
    dut.data_i.value = 0

    # Wait for reset deassertion
    while 1:
        await RisingEdge(dut.clk_i); await Timer(1, units="ps")
        if dut.reset_i == 0: break

    # Main iterations
    i = 0
    while 1:
        await RisingEdge(dut.clk_i); await Timer(1, units="ps")
        # Half chance to send data flit
        if control_random.random() >= 0.5:
            # Assert DUT valid signal
            dut.valid_i.setimmediatevalue(1)
            # Check DUT ready signal
            if dut.ready_and_o == 1:
                # Generate send data
                # dut.data_i.setimmediatevalue(math.floor(data_random.random()*pow(2, WIDTH_P)))
                # dut.data_i.setimmediatevalue(math.floor(data_random.random()*pow(2, ELS_P))*pow(2,WIDTH_P) + math.floor(data_random.random()*pow(2, WIDTH_P)))
                data_input = 0
                for j in range(ELS_P):
                    data_input |= math.floor(data_random.random()*pow(2, WIDTH_P)) << (j*WIDTH_P)
                # print("data_i:", hex(data_input))
                dut.data_i.setimmediatevalue(data_input)

                # iteration increment
                i += 1
                # print("input ITERATION:", i)
                # Check iteration
                if i == ITERATION:
                    # Test finished
                    # print("input break!")
                    break
        else:
            # Deassert DUT valid signal
            dut.valid_i.setimmediatevalue(0)

    await RisingEdge(dut.clk_i); await Timer(1, units="ps")
    # Deassert DUT valid signal
    dut.valid_i.value = 0


async def output_side_testbench(dut, seed):
    """Handle input traffic"""

    # Create local random generator for data generation
    data_random = random.Random()
    data_random.seed(seed)

    # Create control random generator for flow control
    control_random = random.Random()
    control_random.seed(CTRL_OUTPUT_SEED)

    # Initialize DUT interface values
    dut.yumi_i.value = 0

    # Wait for reset deassertion
    while 1:
        await RisingEdge(dut.clk_i); await Timer(1, units="ps")
        if dut.reset_i == 0: break

    # Main iterations
    i = 0
    while 1:
        await RisingEdge(dut.clk_i); await Timer(1, units="ps")
        #####################
        # for j in range(ELS_P):
        j=0
        while j < ELS_P:
            if dut.valid_o.value == 1 and control_random.random() >= 0.5:
                dut.yumi_i.setimmediatevalue(1)
                # print("yumi_i=1")
                test_data = math.floor(data_random.random()*pow(2, WIDTH_P))
                # print("dut.data_o =", hex(dut.data_o.value),", test_data =",hex(test_data))
                assert dut.data_o.value == test_data, "data mismatch!"
                j+=1
            else:
                # Deassert DUT yumi signal
                dut.yumi_i.setimmediatevalue(0)
                # print("yumi_i=0")
            if j < ELS_P:
                # await Timer(CLK_PERIOD*1, units="ps")
                await RisingEdge(dut.clk_i); await Timer(1, units="ps")
            # else:
            #     i+=1
            # await RisingEdge(dut.clk_i); await Timer(1, units="ps")
        i+=1
        # iteration increment
        # i += 1
        print("output ITERATION:", i)
        # Check iteration 
        if i == ITERATION:
            # Test finished
            # print("output break!")
            break
        #####################
        # if dut.valid_o.value == 1 and control_random.random() >= 0.5:
        #     # Assert DUT yumi signal
        #     dut.yumi_i.setimmediatevalue(1)
        #     # Generate check data and compare with receive data
        #     # assert dut.data_o.value == math.floor(data_random.random()*pow(2, WIDTH_P)), "data mismatch!"
        #     for j in range(ELS_P):
        #         # assert dut.data_o.value == dut.data_i.value[i], "data mismatch!"
        #         test_data = math.floor(data_random.random()*pow(2, WIDTH_P))
        #         # print("dut.data_o =", hex(dut.data_o.value),", test_data =",hex(test_data))
        #         assert dut.data_o.value == test_data, "data mismatch!"
        #         if j < ELS_P-1:
        #             # await Timer(CLK_PERIOD*1, units="ps")
        #             await RisingEdge(dut.clk_i); await Timer(1, units="ps")
        #     # iteration increment
        #     i += 1
        #     # print("output ITERATION:", i)
        #     # Check iteration 
        #     if i == ITERATION:
        #         # Test finished
        #         # print("output break!")
        #         break
        # else:
        #     # Deassert DUT yumi signal
        #     dut.yumi_i.setimmediatevalue(0)


    await RisingEdge(dut.clk_i); await Timer(1, units="ps")
    # Deassert DUT yumi signal
    dut.yumi_i.value = 0


@cocotb.test()
async def testbench(dut):
    """Try accessing the design."""

    # Random seed assignment
    seed = time.time()

    # Create a 10ps period clock on DUT port clk_i
    clock = Clock(dut.clk_i, CLK_PERIOD, units="ps")

    # Start the clock. Start it low to avoid issues on the first RisingEdge
    clock_thread = cocotb.start_soon(clock.start(start_high=False))

    # Launch input and output testbench threads
    input_thread = cocotb.start_soon(input_side_testbench(dut, seed))
    output_thread = cocotb.start_soon(output_side_testbench(dut, seed))

    # Reset initialization
    dut.reset_i.value = 1

    # Wait for 5 clock cycles
    await Timer(CLK_PERIOD*5, units="ps")
    await RisingEdge(dut.clk_i); await Timer(1, units="ps")

    # Deassert reset
    dut.reset_i.value = 0

    # Wait for threads to finish
    await input_thread
    await output_thread

    # Wait for 5 clock cycles
    await Timer(CLK_PERIOD*5, units="ps")
    await RisingEdge(dut.clk_i); await Timer(1, units="ps")

    # Assert reset
    dut.reset_i.value = 1

    # Wait for 5 clock cycles
    await Timer(CLK_PERIOD*5, units="ps")

    # Test finished!
    dut._log.info("Test finished! Current reset_i value = %s", dut.reset_i.value)
