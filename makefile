.PHONY: install uninstall

ETC=~/.local/etc
SYSTEMD=~/.config/systemd/user

install:
	mkdir -p ${ETC}/cal-notify
	cp -r ./* ${ETC}/cal-notify
	mkdir -p ${SYSTEMD}
	cp -v ./cal-notify.service ./cal-notify.timer ${SYSTEMD}
	cp -v ./cal-fetch.service ./cal-fetch.timer ${SYSTEMD}
	systemctl --user daemon-reload
	systemctl --user enable --now cal-notify.timer
	systemctl --user enable --now cal-fetch.timer

uninstall:
	systemctl --user stop cal-notify.timer || true
	systemctl --user stop cal-fetch.timer || true
	rm -vf ${SYSTEMD}/cal-notify.service ${SYSTEMD}/cal-notify.timer
	rm -vf ${SYSTEMD}/cal-fetch.service ${SYSTEMD}/cal-fetch.timer
	systemctl --user daemon-reload
	rm -vfr ${ETC}/cal-notify

status:
	systemctl --user status cal-fetch.timer
	systemctl --user status cal-notify.timer
