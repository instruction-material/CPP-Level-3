#include <algorithm>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <string>
#include <vector>


/*****************
*   CONSTANTS   *
*****************/

constexpr int DEBUG_CABLE_ID = 101;
constexpr int SENSOR_KIT_ID = 102;
constexpr int HEX_DRIVER_ID = 103;
constexpr int BREADBOARD_ID = 104;
constexpr int DEBUG_CABLE_QUANTITY = 6;
constexpr int SENSOR_KIT_QUANTITY = 3;
constexpr int HEX_DRIVER_QUANTITY = 10;
constexpr int BREADBOARD_QUANTITY = 8;
constexpr int DUPLICATE_QUANTITY = 1;
const std::string TOOLS_CATEGORY = "tools";
const std::string ELECTRONICS_CATEGORY = "electronics";
const std::string LAB_CATEGORY = "lab";


/*************
*   TYPES   *
*************/

// Store one inventory item row
struct Item {
	int id;
	std::string name;
	std::string category;
	int quantity;
};

// Index inventory rows by id and category
class InventoryIndex {
public:
	/**
	 * @brief Add one item when its id is not already present
	 *
	 * @param item Item to add
	 *
	 * @return True when the item is accepted
	 */
	bool add(const Item& item) {
		// Reject duplicate item ids
		if (id_to_index_.count(item.id) > 0) {
			return false;
		}

		id_to_index_[item.id] = items_.size();
		categories_.insert(item.category);
		items_.push_back(item);
		return true;
	}

	/**
	 * @brief Select all items in one category
	 *
	 * @param category Category to select
	 *
	 * @return Items that match the category
	 */
	std::vector<Item> select_category(const std::string& category) const {
		std::vector<Item> selected;

		// Copy every row in the requested category
		for (const Item& item : items_) {
			if (item.category == category) {
				selected.push_back(item);
			}
		}

		return selected;
	}

	/**
	 * @brief Project item names from selected rows
	 *
	 * @param rows Rows to project
	 *
	 * @return Sorted item names
	 */
	std::vector<std::string> project_names(const std::vector<Item>& rows) const {
		std::vector<std::string> names;

		// Collect names from every provided row
		for (const Item& item : rows) {
			names.push_back(item.name);
		}

		std::sort(names.begin(), names.end());
		return names;
	}

	/**
	 * @brief Rename one category across the inventory
	 *
	 * @param from Category name to replace
	 *
	 * @param to Replacement category name
	 *
	 * @return True when at least one item changed
	 */
	bool rename_category(const std::string& from, const std::string& to) {
		bool changed = false;

		// Update every item that belongs to the source category
		for (Item& item : items_) {
			if (item.category == from) {
				item.category = to;
				changed = true;
			}
		}

		// Rebuild category lookup only when a rename happened
		if (changed) {
			rebuild_category_index();
		}

		return changed;
	}

	/**
	 * @brief Join inventory rows with supplier names by id
	 *
	 * @param supplier_by_id Supplier lookup keyed by item id
	 *
	 * @return Joined display rows
	 */
	std::vector<std::string> join_suppliers(const std::map<int, std::string>& supplier_by_id) const {
		std::vector<std::string> joined;

		// Build one joined row for each item with a known supplier
		for (const Item& item : items_) {
			const auto supplier = supplier_by_id.find(item.id);

			// Skip items that do not have supplier data
			if (supplier == supplier_by_id.end()) {
				continue;
			}

			std::ostringstream row;
			row << item.id << " | " << item.name << " | " << item.quantity << " | " << supplier->second;
			joined.push_back(row.str());
		}

		return joined;
	}

	/**
	 * @brief Print all known categories
	 */
	void print_categories() const {
		std::cout << "Categories:";

		// Print categories in set order
		for (const std::string& category : categories_) {
			std::cout << ' ' << category;
		}

		std::cout << "\n";
	}

private:
	// Rebuild the category set from current items
	void rebuild_category_index() {
		categories_.clear();

		// Insert each current item category
		for (const Item& item : items_) {
			categories_.insert(item.category);
		}
	}

	std::vector<Item> items_;
	std::map<int, std::size_t> id_to_index_;
	std::set<std::string> categories_;
};


/*****************
*   FUNCTIONS   *
*****************/

// Add sample rows to the inventory
void load_sample_inventory(InventoryIndex& inventory) {
	inventory.add({DEBUG_CABLE_ID, "debug cable", TOOLS_CATEGORY, DEBUG_CABLE_QUANTITY});
	inventory.add({SENSOR_KIT_ID, "sensor kit", ELECTRONICS_CATEGORY, SENSOR_KIT_QUANTITY});
	inventory.add({HEX_DRIVER_ID, "hex driver", TOOLS_CATEGORY, HEX_DRIVER_QUANTITY});
	inventory.add({BREADBOARD_ID, "breadboard", ELECTRONICS_CATEGORY, BREADBOARD_QUANTITY});
}

// Build sample supplier data keyed by item id
std::map<int, std::string> build_suppliers() {
	return {
		{DEBUG_CABLE_ID, "North Lab"},
		{SENSOR_KIT_ID, "Circuit House"},
		{HEX_DRIVER_ID, "North Lab"},
		{BREADBOARD_ID, "Circuit House"},
	};
}

/**
 * @brief Run the inventory indexer demonstration
 *
 * @return Process exit code
 */
int main() {
	InventoryIndex inventory;
	load_sample_inventory(inventory);

	std::cout
		<< "Duplicate accepted? "
		<< (inventory.add({DEBUG_CABLE_ID, "duplicate", TOOLS_CATEGORY, DUPLICATE_QUANTITY}) ? "yes" : "no")
		<< "\n";

	inventory.print_categories();

	const auto tools = inventory.select_category(TOOLS_CATEGORY);
	const auto names = inventory.project_names(tools);
	std::cout << "Tool names:";

	// Print selected tool names in sorted order
	for (const std::string& name : names) {
		std::cout << ' ' << name;
	}

	std::cout << "\n";

	inventory.rename_category(ELECTRONICS_CATEGORY, LAB_CATEGORY);
	inventory.print_categories();

	const auto suppliers = build_suppliers();

	// Print each inventory row joined to supplier data
	for (const std::string& row : inventory.join_suppliers(suppliers)) {
		std::cout << row << "\n";
	}
}
