PROJECT_DIR=$(PWD)
WARPSHELL=xilinx_u250_xdma_gen3x8_exp
PERSONA=default

synth:
	rm -rf ./build/
	mkdir -p ./build/
	cd ./build/;
	vivado -mode batch -source ./synth.tcl


impl: 
	vivado -mode batch -source ./impl.tcl; \
	mv user.bin user.bin.tmp; \
	xxd -e -g4 user.bin.tmp | xxd -r > user.bin; \
	rm user.bin.tmp

clean:
	rm -rf ./build
