import brian2
import collections

def parse_namespace(namespace_dict: dict):
    """evaluates a string as a quantity
    Args:
        namespace_dict: 
    Return:
        {name, quantity}
    """
    return {
        name : eval(
            quantity,
            brian2.core.namespace.DEFAULT_UNITS
        ) for name, quantity in namespace_dict.items()
    }

def load_neurongroups(neuron_model: str, neuron_params_dict: dict, **neuron_keyargs):
    """
    Args:
        neuron_model: neuron descriptions as parsable as brian2.equation
        neuron_params_dict: {parameter_name: }
        neuron_keyargs: keyargs to set all brian2.NeuronGroup
    Return:
        {group_name: brian2.NeuronGroup}
    """
    return {
        neuron_name : brian2.NeuronGroup(
            neuron_params.pop('N'),
            neuron_model,
            name=neuron_name,
            namespace = parse_namespace(
                neuron_params.pop('namespace') if 'namespace' in neuron_params else dict()
            ),
            **neuron_params,
            **neuron_keyargs
        ) for neuron_name, neuron_params in neuron_params_dict.items()
    }

def load_synapses(neurongroup_dict: dict, synapse_model_dict: dict, synapse_params_dict3: dict):
    """
    Args:
        neurongroup_dict: {group_name: brian2.NeuronGroup} parsed by load_neurongroups
        synapse_model_dict: {synapse_type_name: synapse_model}
            synapse_model: 
        synapse_params_dict3: {synapse_type_name: {from_neuron_name: {to_neuron_name: synapse_params}}}
            synapse_params:
    Return:
        [brian2.Synapses, brian2.Synapses, ...]
    """
    synapse_list = list()

    for synapse_type_name, synapse_model in synapse_model_dict.items():
        synapse_model_namespace = synapse_model.pop('namespace') if 'namespace' in synapse_model else dict()

        for from_neuron_name, synapse_params_dict in synapse_params_dict3[synapse_type_name].items():
            for to_neuron_name, synapse_params in synapse_params_dict.items():
                synapse_namespace = parse_namespace(
                    dict(
                        synapse_params.pop('namespace') if 'namespace' in synapse_params else dict(),
                        **synapse_model_namespace
                    )
                )
                synapse = brian2.Synapses(
                    neurongroup_dict[from_neuron_name],
                    neurongroup_dict[to_neuron_name],
                    name='{}_from{}to{}'.format(
                        synapse_type_name,
                        ''.join(filter(str.isupper, from_neuron_name)),
                        ''.join(filter(str.isupper, to_neuron_name))
                        #TODO: separate naming rule
                    ),
                    namespace=synapse_namespace,
                    **synapse_model
                )
                synapse_list.append(synapse)
                synapse.connect(**synapse_params)
    return synapse_list

if __name__ == '__main__':
    #TODO: write tests
    pass