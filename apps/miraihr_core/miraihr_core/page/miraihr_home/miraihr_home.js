frappe.pages["miraihr_home"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Welcome to MiraiHR"),
		single_column: true,
	});
	page.main.addClass("miraihr-home");
	const content = document.createElement("section");
	content.className = "miraihr-home__content";
	content.setAttribute("aria-live", "polite");
	content.textContent = __("Loading your workspace…");
	page.main[0].appendChild(content);

	frappe.call("miraihr_core.api.get_navigation").then(({ message = [] }) => {
		content.replaceChildren();
		if (!message.length) {
			const empty = document.createElement("p");
			empty.textContent = __("No MiraiHR workspaces are available for your account.");
			content.appendChild(empty);
			return;
		}

		const heading = document.createElement("h2");
		heading.textContent = __("Your workspaces");
		content.appendChild(heading);
		const list = document.createElement("nav");
		list.className = "miraihr-home__grid";
		list.setAttribute("aria-label", __("MiraiHR workspaces"));
		message.forEach(({ label, route }) => {
			const link = document.createElement("a");
			link.className = "miraihr-home__card";
			link.href = route;
			const title = document.createElement("span");
			title.textContent = __(label);
			link.appendChild(title);
			list.appendChild(link);
		});
		content.appendChild(list);
	}).catch(() => {
		content.textContent = __("Your workspace could not be loaded. Refresh the page or contact your administrator.");
	});
};
