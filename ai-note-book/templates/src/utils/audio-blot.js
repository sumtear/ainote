// src/utils/AudioBlot.js
import Quill from 'quill';

const Inline = Quill.import('blots/inline');

class AudioBlot extends Inline {
    static create(value) {
        let node = super.create();
        node.setAttribute('controls', true);
        node.setAttribute('src', value);
        return node;
    }

    static value(node) {
        return node.getAttribute('src');
    }

    static formats(node) {
        return node.getAttribute('src');
    }

    format(name, value) {
        if (name === 'audio' && value) {
            this.domNode.setAttribute('src', value);
        } else {
            super.format(name, value);
        }
    }
}

AudioBlot.blotName = 'audio';
AudioBlot.tagName = 'audio';

export default AudioBlot;