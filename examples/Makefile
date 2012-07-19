WORKDIR	?= /tmp/jinja2-cui.examples.d
#render	?= jinja2-cui -D
render	?= jinja2-cui

# quick hack:
define yaml2json =
python -c 'import sys,json,yaml; json.dump(yaml.load(open(sys.argv[1])), open(sys.argv[2], "w"), indent=2)'
endef

objs = \
$(WORKDIR)/0_single_template_and_config.out \
$(WORKDIR)/1_single_template_and_multi_configs.out \
$(WORKDIR)/2_single_template_and_multi_configs.out \
$(WORKDIR)/3_single_template_and_multi_configs.out \
$(WORKDIR)/5_multi_templates_and_multi_configs.out \
$(WORKDIR)/6_multi_templates_and_multi_configs.out \
$(NULL)

all: $(objs)



$(WORKDIR):
	mkdir -p $@

$(objs): $(WORKDIR)


$(WORKDIR)/0_single_template_and_config.out: a.yaml
$(WORKDIR)/0_single_template_and_config.out: a.t
	@echo "case #0: single template and single config"
	$(render) -C a.yaml $< -o $@

$(WORKDIR)/1_single_template_and_multi_configs.out: a.yaml
$(WORKDIR)/1_single_template_and_multi_configs.out: b.yaml
$(WORKDIR)/1_single_template_and_multi_configs.out: a.t
	@echo "case #1: single template and multiple configs (yaml only)"
	$(render) -C a.yaml,b.yaml $< -o $@

$(WORKDIR)/b.json: b.yaml
	$(yaml2json) $< $@

$(WORKDIR)/2_single_template_and_multi_configs.out: a.yaml
$(WORKDIR)/2_single_template_and_multi_configs.out: $(WORKDIR)/b.json
$(WORKDIR)/2_single_template_and_multi_configs.out: a.t
	@echo "case #2: single template and multiple configs (yaml and json)"
	$(render) -C a.yaml,$(WORKDIR)/b.json $< -o $@

$(WORKDIR)/b.dat: $(WORKDIR)/b.json
	cp -f $< $@

$(WORKDIR)/3_single_template_and_multi_configs.out: a.yaml
$(WORKDIR)/3_single_template_and_multi_configs.out: $(WORKDIR)/b.dat
$(WORKDIR)/3_single_template_and_multi_configs.out: a.t
	@echo "case #3: single template and multiple configs (yaml and json w/o file ext)"
	$(render) -C a.yaml,json:$(WORKDIR)/b.dat $< -o $@


$(WORKDIR)/5_multi_templates_and_multi_configs.out: a.yaml
$(WORKDIR)/5_multi_templates_and_multi_configs.out: b.yaml
$(WORKDIR)/5_multi_templates_and_multi_configs.out: c.yaml
$(WORKDIR)/5_multi_templates_and_multi_configs.out: a.includee.t
$(WORKDIR)/5_multi_templates_and_multi_configs.out: a.t
	@echo "case #5: multiple templates (master and includee; w/o explicit template paths) and multiple configs (yaml only)"
	$(render) -C a.yaml,b.yaml,c.yaml $< -o $@

$(WORKDIR)/b.includee.t: a.includee.t
	cp -f $< $@

$(WORKDIR)/6_multi_templates_and_multi_configs.out: a.yaml
$(WORKDIR)/6_multi_templates_and_multi_configs.out: b.yaml
$(WORKDIR)/6_multi_templates_and_multi_configs.out: d.yaml
$(WORKDIR)/6_multi_templates_and_multi_configs.out: $(WORKDIR)/b.includee.t
$(WORKDIR)/6_multi_templates_and_multi_configs.out: a.t
	@echo "case #5: multiple templates (master and includee; w/o explicit template paths) and multiple configs (yaml only)"
	$(render) -C a.yaml,b.yaml,d.yaml -T $(WORKDIR) $< -o $@

clean:
	@echo "cleanup ..."

.PHONY: clean
