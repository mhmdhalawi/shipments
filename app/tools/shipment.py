from models.shipment import ShipmentStatus


SHIPMENT: list = [
    {
        "name": "get_all_shipments",
        "description": "Retrieve all shipments from the database.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_shipment_by_id",
        "description": "Retrieve a single shipment by its ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "shipment_id": {
                    "type": "string",
                    "description": "The UUID of the shipment",
                }
            },
            "required": ["shipment_id"],
        },
    },
    {
        "name": "get_shipments_by_status",
        "description": "Retrieve all shipments with a specific status.",
        "input_schema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": [s.value for s in ShipmentStatus],
                    "description": "The status to filter by",
                }
            },
            "required": ["status"],
        },
    },
    {
        "name": "create_shipment",
        "description": "Create a new shipment with given content and weight.",
        "input_schema": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "Description of the shipment content",
                },
                "weight": {
                    "type": "number",
                    "description": "Weight of the shipment in kg",
                },
            },
            "required": ["content", "weight"],
        },
    },
    {
        "name": "update_shipment",
        "description": "Update an existing shipment's details.",
        "input_schema": {
            "type": "object",
            "properties": {
                "shipment_id": {
                    "type": "string",
                    "description": "The UUID of the shipment to update",
                },
                "content": {
                    "type": "string",
                    "description": "New description of the shipment content",
                },
                "weight": {
                    "type": "number",
                    "description": "New weight of the shipment in kg",
                },
                "status": {
                    "type": "string",
                    "enum": [s.value for s in ShipmentStatus],
                    "description": "New status of the shipment",
                },
            },
            "required": ["shipment_id"],
        },
    },
    {
        "name": "delete_shipment",
        "description": "Delete a shipment by its ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "shipment_id": {
                    "type": "string",
                    "description": "The UUID of the shipment to delete",
                }
            },
            "required": ["shipment_id"],
        },
    },
]
