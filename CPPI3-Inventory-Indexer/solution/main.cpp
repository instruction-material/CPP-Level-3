#include <algorithm>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <string>
#include <vector>

struct Item {
	int id;
	std::string name;
	std::string category;
	int quantity;
};

class InventoryIndex {
public:
	bool add(const Item& item) {
		if (idToIndex_.count(item.id) > 0) {
			return false;
		}

		idToIndex_[item.id] = items_.size();
		categories_.insert(item.category);
		items_.push_back(item);
		return true;
	}

	std::vector<Item> selectCategory(const std::string& category) const {
		std::vector<Item> selected;
		for (const Item& item : items_) {
			if (item.category == category) {
				selected.push_back(item);
			}
		}
		return selected;
	}

	std::vector<std::string> projectNames(const std::vector<Item>& rows) const {
		std::vector<std::string> names;
		for (const Item& item : rows) {
			names.push_back(item.name);
		}
		std::sort(names.begin(), names.end());
		return names;
	}

	bool renameCategory(const std::string& from, const std::string& to) {
		bool changed = false;
		for (Item& item : items_) {
			if (item.category == from) {
				item.category = to;
				changed = true;
			}
		}

		if (changed) {
			rebuildCategoryIndex();
		}
		return changed;
	}

	std::vector<std::string> joinSuppliers(const std::map<int, std::string>& supplierById) const {
		std::vector<std::string> joined;
		for (const Item& item : items_) {
			const auto supplier = supplierById.find(item.id);
			if (supplier == supplierById.end()) {
				continue;
			}

			std::ostringstream row;
			row << item.id << " | " << item.name << " | " << item.quantity << " | " << supplier->second;
			joined.push_back(row.str());
		}
		return joined;
	}

	void printCategories() const {
		std::cout << "Categories:";
		for (const std::string& category : categories_) {
			std::cout << ' ' << category;
		}
		std::cout << "\n";
	}

private:
	void rebuildCategoryIndex() {
		categories_.clear();
		for (const Item& item : items_) {
			categories_.insert(item.category);
		}
	}

	std::vector<Item> items_;
	std::map<int, std::size_t> idToIndex_;
	std::set<std::string> categories_;
};

int main() {
	InventoryIndex inventory;
	inventory.add({ 101, "debug cable", "tools", 6 });
	inventory.add({ 102, "sensor kit", "electronics", 3 });
	inventory.add({ 103, "hex driver", "tools", 10 });
	inventory.add({ 104, "breadboard", "electronics", 8 });
	std::cout << "Duplicate accepted? " << (inventory.add({ 101, "duplicate", "tools", 1 }) ? "yes" : "no") << "\n";

	inventory.printCategories();

	const auto tools = inventory.selectCategory("tools");
	const auto names = inventory.projectNames(tools);
	std::cout << "Tool names:";
	for (const std::string& name : names) {
		std::cout << ' ' << name;
	}
	std::cout << "\n";

	inventory.renameCategory("electronics", "lab");
	inventory.printCategories();

	const std::map<int, std::string> suppliers {
		{ 101, "North Lab" },
		{ 102, "Circuit House" },
		{ 103, "North Lab" },
		{ 104, "Circuit House" },
	};
	for (const std::string& row : inventory.joinSuppliers(suppliers)) {
		std::cout << row << "\n";
	}
}
