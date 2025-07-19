let result = {
    // scan accomplishments
    accomplishments: [ // length always 3
        {
            title: ``, // str (phrase, 7 words max)
            body: ``, // str
        },
    ],

    // scan momentum
    history: {
        lastScan: [ // length: 1-5
            {
                hasImplemented: NaN, // bool
                title: ``, // str
            },
        ],
        team: [ // length: 1-5
            {
                hasImplemented: NaN, // bool
                title: ``, // str
            },
        ],
        overall: [ // length: 1-5
            {
                hasImplemented: NaN, // bool
                title: ``, // str
            },
        ],
    },

    // reasoning feedback for scan
    reasoning: {
        perspectives: [ // length: 1-3
            {
                title: ``, // str (phrase, 7 words max)
                evidence: ``, // str
                impact: ``, // str
                next: ``, // str
                questions: ``, // str
            },
        ],
        assumptions: [
            {
                title: ``, // str (phrase, 7 words max)
                evidence: ``, // str
                impact: ``, // strk0
                next: ``, // str
                questions: ``, // str
            },
        ],
        logic: [
            {
                title: ``, // str (phrase, 7 words max)
                evidence: ``, // str
                impact: ``, // str
                next: ``, // str
                questions: ``, // str
            },
        ],
        creativity: [
            {
                title: ``, // str (phrase, 7 words max)
                evidence: ``, // str
                impact: ``, // str
                next: ``, // str
                questions: ``, // str
            },
        ],
    },

    // next steps for scan
    next: {
        comp: [ // length: 5-10, list of action recs summarized from score feedback
            {
                title: ``, // str (phrase, 7 words max)
                body: ``, // str
            },
        ],
        crit: [
            {
                title: ``, // str (phrase, 7 words max)
                body: ``, // str
            },
        ],
        // other stuff but not focus rn
    },

    // scores w/ feedback for each construct/skill (across scan)
    scores: {
        c0: { // central construct
            id: NaN, // construct id (type: number)
            icon: ``, // tabler svg code for icon (type: string)
            title: `Neural Power`, // construct title (type: string, default: Neural Power, ``-able)
            num: {
                low: NaN, // lower limit raw score (type: num)
                mid: NaN, // most likely raw score (type: num)
                high: NaN, // upper limit raw score (type: num)
            },
            theme: {
                color: {
                    text: ``, // hex color for icon/level (type: string)
                    highlight: ``, // hex color for radar/theme (type: string)
                    contrast: ``, // hex color for contrast to highlight (type: string)
                },
            },
            explanation: ``, // explanation for score (type: string)
            feedback: { // feedback for this construct
                compliments: {
                    tiles: [ // length: 1-3
                        /*
                        { // aggregate num/text
                            id: ``, // comp id encrypted (type: str)
                            title: ``, // comp title (type: str)
                            num: NaN, // comp freq num (type: num)
                            what: ``, // comp what/where detail (type: str)
                            why: ``, // comp importance (type: str)
                            action: ``, // what to do in life (type: str)
                            que: ``, // questions to ask in life (type: str)
                        },
                        */
                    ],
                },
                criticisms: {
                    tiles: [ // length: 1-3
                        /*
                        { // aggregate num/text
                            id: ``, // crit id encrypted (type: str)
                            title: ``, // crit title (type: str)
                            num: NaN, // crit freq num (type: num)
                            what: ``, // crit what/where detail (type: str)
                            why: ``, // crit importance (type: str)
                            action: ``, // what to do in life (type: str)
                            que: ``, // questions to ask in life (type: str)
                        },
                        */
                    ],
                },
            },
            subConstructs: [ // likely length == 3
                {
                    id: NaN, // construct id (type: number)
                    icon: ``, // tabler svg code for icon (type: string)
                    title: ``, // construct title (type: string, ``-able)
                    num: {
                        low: NaN, // lower limit raw score (type: num)
                        mid: NaN, // most likely raw score (type: num)
                        high: NaN, // upper limit raw score (type: num)
                    },
                    theme: {
                        color: {
                            text: ``, // hex color for icon/level (type: string)
                            highlight: ``, // hex color for radar/theme (type: string)
                            contrast: ``, // hex color for contrast to highlight (type: string)
                        },
                    },
                    explanation: ``, // explanation for score (type: string)
                    feedback: {
                        compliments: {
                            tiles: [ // length: 1-3
                                /*
                                { // aggregate num/text
                                    id: ``, // comp id encrypted (type: str)
                                    title: ``, // comp title (type: str)
                                    num: NaN, // comp freq num (type: num)
                                    what: ``, // comp what/where detail (type: str)
                                    why: ``, // comp importance (type: str)
                                    action: ``, // what to do in life (type: str)
                                    que: ``, // questions to ask in life (type: str)
                                },
                                */
                            ],
                        },
                        criticisms: {
                            tiles: [ // length: 1-3
                                /*
                                { // aggregate num/text
                                    id: ``, // crit id encrypted (type: str)
                                    title: ``, // crit title (type: str)
                                    num: NaN, // crit freq num (type: num)
                                    what: ``, // crit what/where detail (type: str)
                                    why: ``, // crit importance (type: str)
                                    action: ``, // what to do in life (type: str)
                                    que: ``, // questions to ask in life (type: str)
                                },
                                */
                            ],
                        },
                    },
                    subConstructs: [ // unknown/arbitrary # of subconstructs
                        {
                            icon: ``, // tabler svg code for icon (type: string)
                            title: ``, // construct title (type: string, ``-able)
                            num: {
                                low: NaN, // lower limit raw score (type: num)
                                mid: NaN, // most likely raw score (type: num)
                                high: NaN, // upper limit raw score (type: num)
                            },
                            theme: {
                                color: {
                                    text: ``, // hex color for icon/level (type: string)
                                    highlight: ``, // hex color for radar/theme (type: string)
                                    contrast: ``, // hex color for contrast to highlight (type: string)
                                },
                            },
                            explanation: ``, // explanation for score (type: string)
                            feedback: {
                                compliments: {
                                    tiles: [ // length: 1-3
                                        /*
                                        { // aggregate num/text
                                            id: ``, // comp id encrypted (type: str)
                                            title: ``, // comp title (type: str)
                                            num: NaN, // comp freq num (type: num)
                                            what: ``, // comp what/where detail (type: str)
                                            why: ``, // comp importance (type: str)
                                            action: ``, // what to do in life (type: str)
                                            que: ``, // questions to ask in life (type: str)
                                        },
                                        */
                                    ],
                                },
                                criticisms: {
                                    tiles: [ // length: 1-3
                                        /*
                                        { // aggregate num/text
                                            id: ``, // crit id encrypted (type: str)
                                            title: ``, // crit title (type: str)
                                            num: NaN, // crit freq num (type: num)
                                            what: ``, // crit what/where detail (type: str)
                                            why: ``, // crit importance (type: str)
                                            action: ``, // what to do in life (type: str)
                                            que: ``, // questions to ask in life (type: str)
                                        },
                                        */
                                    ],
                                },
                            },
                            subConstructs: [], // likely empty
                        },
                    ],
                },
            ],
        },
    },

    // round feedback/scores (not including scan result data)
    scan: {
        rounds: [ // arbitrarily long (1 per round)
            {
                hasScore: NaN, // some rounds may not show score (type: bool)
                hasFeedback: NaN, // some rounds may not show feedback (type: bool)
                scores: {
                    c0: { // central construct
                        id: NaN, // construct id (type: number)
                        icon: ``, // tabler svg code for icon (type: string)
                        title: `Neural Power`, // construct title (type: string, default: Neural Power, ``-able)
                        num: {
                            mid: NaN, // most likely raw score (type: num)
                        },
                        theme: {
                            color: {
                                text: ``, // hex color for icon/level (type: string)
                                highlight: ``, // hex color for radar/theme (type: string)
                                contrast: ``, // hex color for contrast to highlight (type: string)
                            },
                        },
                        explanation: ``, // explanation for score (type: string)
                    },
                },
                feedback: { // feedback across all constructs
                    compliments: {
                        tiles: [ // length: 1-3
                            /*
                            { // aggregate num/text
                                id: ``, // comp id encrypted (type: str)
                                title: ``, // comp title (type: str)
                                num: NaN, // comp freq num (type: num)
                                what: ``, // comp what/where detail (type: str)
                                why: ``, // comp importance (type: str)
                                action: ``, // what to do in life (type: str)
                                que: ``, // questions to ask in life (type: str)
                            },
                            */
                        ],
                    },
                    criticisms: {
                        tiles: [ // length: 1-3
                            /*
                            { // aggregate num/text
                                id: ``, // crit id encrypted (type: str)
                                title: ``, // crit title (type: str)
                                num: NaN, // crit freq num (type: num)
                                what: ``, // crit what/where detail (type: str)
                                why: ``, // crit importance (type: str)
                                action: ``, // what to do in life (type: str)
                                que: ``, // questions to ask in life (type: str)
                            },
                            */
                        ],
                    },
                },
            },
        ],
    },
};