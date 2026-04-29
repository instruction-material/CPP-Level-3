#include <algorithm>
#include <iostream>
#include <map>
#include <set>
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
		// TODO: Return only the rows whose category matches the argument.
		(void) category;
		return {};
	}

	std::vector<std::string> projectNames(const std::vector<Item>& rows) const {
		// TODO: Return the item names from rows in sorted order.
		(void) rows;
		return {};
	}

	std::vector<std::string> joinSuppliers(const std::map<int, std::string>& supplierById) const {
		// TODO: Combine each known inventory row with its supplier name.
		(void) supplierById;
		return {};
	}

	void printCategories() const {
		std::cout << "Categories:";
		for (const std::string& category : categories_) {
			std::cout << ' ' << category;
		}
		std::cout << "\n";
	}

private:
	std::vector<Item> items_;
	std::map<int, std::size_t> idToIndex_;
	std::set<std::string> categories_;
};

int main() {
	InventoryIndex inventory;
	inventory.add({ 101, "debug cable", "tools", 6 });
	inventory.add({ 102, "sensor kit", "electronics", 3 });
	inventory.add({ 103, "hex driver", "tools", 10 });

	inventory.printCategories();

	const auto tools = inventory.selectCategory("tools");
	const auto names = inventory.projectNames(tools);
	std::cout << "Tool names:";
	for (const std::string& name : names) {
		std::cout << ' ' << name;
	}
	std::cout << "\n";

	const std::map<int, std::string> suppliers {
		{ 101, "North Lab" },
		{ 102, "Circuit House" },
		{ 103, "North Lab" },
	};
	for (const std::string& row : inventory.joinSuppliers(suppliers)) {
		std::cout << row << "\n";
	}
}
