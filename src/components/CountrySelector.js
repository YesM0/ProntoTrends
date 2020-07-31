import React from 'react';

function CountrySelector({handleCountryChange, value}) {
    return (
        <select
            className={'input'} onChange={handleCountryChange} value={value}>
            <option value={'Germany'}>Germany</option>
            <option value={'Italy'}>Italy</option>
            <option value={'France'}>France</option>
            <option value={'Spain'}>Spain</option>
            <option value={'Austria'}>Austria</option>
            <option value={'Switzerland'}>Switzerland</option>
        </select>
    );
}

export default CountrySelector;