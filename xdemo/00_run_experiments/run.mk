
Ms := $(shell seq 200 50 400)
Ns := $(shell seq 200 50 400)
Ks := $(shell seq 200 50 400)

targets := $(foreach M,$(Ms),$(foreach N,$(Ns),$(foreach K,$(Ks),out/out_$(M)_$(N)_$(K).txt)))

all : $(targets)

define rule
out/out_$(M)_$(N)_$(K).txt : out/created
	./mm $(M) $(N) $(K) > $$@
endef

out/created :
	mkdir -p $@

$(foreach M,$(Ms),$(foreach N,$(Ns),$(foreach K,$(Ks),$(eval $(call rule)))))
