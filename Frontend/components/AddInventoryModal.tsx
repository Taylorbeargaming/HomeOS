type AddInventoryModalProps = {
    isOpen: boolean;
    onClose: () => void;
};



export default function AddInventoryModal({
    isOpen,
    onClose,
}: AddInventoryModalProps) {

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center">

            <div className="bg-white rounded-xl p-6 w-full max-w-md shadow-lg">

                <h2 className="text-2xl font-bold mb-6 text-black">
                    Add Inventory Item
                </h2>

                <p className="text-gray-600 mb-6">
                    Form coming next...
                </p>

                <div className="flex justify-end">
                    <button
                        onClick={onClose}
                        className="bg-gray-500 text-white px-4 py-2 rounded"
                    >
                        Close
                    </button>
                </div>

            </div>

        </div>
    );
}

