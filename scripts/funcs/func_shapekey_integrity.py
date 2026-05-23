import bpy


def validate_shape_key_lengths(obj, log_prefix="shape_key_integrity"):
    if obj is None or obj.type != 'MESH' or obj.data is None:
        return False
    if obj.data.shape_keys is None:
        return True

    vertex_count = len(obj.data.vertices)
    for key_block in obj.data.shape_keys.key_blocks:
        if len(key_block.data) != vertex_count:
            print(
                f"[{log_prefix}] Invalid vertex count on '{obj.name}' "
                f"shape key '{key_block.name}': {len(key_block.data)} vs mesh {vertex_count}"
            )
            return False
    return True


def resolve_relative_key_by_name(key_blocks, relative_key_name):
    if len(key_blocks) == 0:
        return None

    basis = key_blocks[0]
    if not relative_key_name:
        return basis

    for key_block in key_blocks:
        if key_block.name == relative_key_name:
            return key_block
    return basis


def ensure_shape_key_integrity(obj, log_prefix="shape_key_integrity"):
    if obj is None or obj.type != 'MESH' or obj.data is None:
        return True

    if not validate_shape_key_lengths(obj, log_prefix=log_prefix):
        return False

    normalize_relative_keys(obj, log_prefix=log_prefix)
    return validate_shape_key_lengths(obj, log_prefix=log_prefix)


def normalize_relative_keys(obj, log_prefix="shape_key_integrity"):
    if obj is None or obj.type != 'MESH' or obj.data is None:
        return 0

    shape_keys = obj.data.shape_keys
    if shape_keys is None:
        return 0

    key_blocks = shape_keys.key_blocks
    if len(key_blocks) <= 1:
        return 0

    basis = key_blocks[0]
    fixed_count = 0

    for key_block in key_blocks[1:]:
        relative_name = None
        try:
            if key_block.relative_key is not None:
                relative_name = key_block.relative_key.name
        except ReferenceError:
            relative_name = None

        if relative_name == key_block.name:
            relative_name = None

        resolved = resolve_relative_key_by_name(key_blocks, relative_name)

        try:
            if key_block.relative_key is not resolved:
                key_block.relative_key = resolved
                fixed_count += 1
        except ReferenceError:
            key_block.relative_key = resolved
            fixed_count += 1

    if fixed_count:
        print(f"[{log_prefix}] normalized {fixed_count} relative keys on '{obj.name}'")
    return fixed_count
