.PHONY: install uninstall status

INSTALL_DIR=~/.local/lib/cal-notify
SYSTEMD=~/.config/systemd/user

install:
	mkdir -p ${INSTALL_DIR} ${INSTALL_DIR}/calendars
	cp -r \
		./cal-fetch.sh \
		./cal-notify.sh \
		./get-next-events.py \
		./calendars.txt \
		${INSTALL_DIR}
	mkdir -p ${SYSTEMD}
	cp -v \
		./cal-fetch.service \
		./cal-fetch.timer \
		./cal-notify.service \
		./cal-notify.timer \
		${SYSTEMD}
	systemctl --user daemon-reload
	systemctl --user enable --now \
		cal-notify.timer \
		cal-fetch.timer

uninstall:
	systemctl --user stop \
		cal-notify.timer \
		cal-fetch.timer || true
	rm -vf \
		${SYSTEMD}/cal-fetch.service \
		${SYSTEMD}/cal-fetch.timer \
		${SYSTEMD}/cal-notify.service \
		${SYSTEMD}/cal-notify.timer
	systemctl --user daemon-reload
	rm -vfr ${INSTALL_DIR}

status:
	systemctl --user --no-pager status \
		cal-fetch.service \
		cal-fetch.timer \
		cal-notify.service \
		cal-notify.timer || true
